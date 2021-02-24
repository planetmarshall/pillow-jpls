#include <charls/charls.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <fmt/format.h>

#include <vector>

namespace py = pybind11;
using namespace py::literals;

namespace pybind11 {

// Bytes object that supports resizing and the buffer protocol
class bytes_ : public buffer {
  public:
  PYBIND11_OBJECT_CVT(bytes_, buffer, PyBytes_Check, PyBytes_FromObject)

    bytes_(const char *c, size_t n)
        : buffer(PyBytes_FromStringAndSize(c, (ssize_t) n), stolen_t{}) {
        if (!m_ptr) pybind11_fail("Could not allocate bytes object!");
    }

    bytes_()
        : bytes_("", 0) {
    }

    void resize(size_t len) { _PyBytes_Resize(&m_ptr, len); }

    size_t size() const { return static_cast<size_t>(PyByteArray_Size(m_ptr)); }

    explicit operator std::string() const {
        char *buffer = PyByteArray_AS_STRING(m_ptr);
        ssize_t size = PyByteArray_GET_SIZE(m_ptr);
        return std::string(buffer, static_cast<size_t>(size));
    }
};
}


template<typename T>
T value_or(const py::dict & kwargs, const char * key, const T & default_value) {
    if (kwargs.template contains(key)) {
        return kwargs[key].cast<T>();
    }

    return default_value;
}

charls::interleave_mode interleave_mode(const py::dict & kwargs) {
    if (!kwargs.contains("interleave")) {
        return charls::interleave_mode::sample;
    }

    auto mode = kwargs["interleave"].cast<std::string>();
    if (mode == "none") {
        return charls::interleave_mode::none;
    }
    if (mode == "sample") {
        return charls::interleave_mode::sample;
    }
    if (mode == "line") {
        return charls::interleave_mode::line;
    }
    throw std::runtime_error(fmt::format(FMT_STRING("interleave mode '{}' not recognized"), mode));
}

constexpr int32_t clamp(int32_t i, int32_t j, int32_t maxval) {
    if (i > maxval) {
        return j;
    }
    if (i < j) {
        return j;
    }
    return i;
}

charls::jpegls_pc_parameters preset_coding_parameters(const py::dict & kwargs, int32_t bits_per_sample, int32_t near) {
    // Defaults have to be set for all the parameters, or they all need to be set to zero
    // so we handle missing defaults here - see https://github.com/team-charls/charls/issues/84
    charls::jpegls_pc_parameters params{0, 0, 0, 0, 0};
    const std::vector<std::string> keys{ "maxval", "t1", "t2", "t3", "reset" };
    auto iter = std::find_first_of(
        kwargs.begin(),
        kwargs.end(),
        keys.begin(),
        keys.end(),
        []( const auto & param, const auto & key) {
            return key == std::string(py::str(param.first));
        });

    if (iter == kwargs.end() && bits_per_sample <= 12) {
        return params;
    }

    params.maximum_sample_value = value_or<int32_t>(kwargs, "maxval", std::pow(2, bits_per_sample) - 1);
    params.reset_value = value_or<int32_t>(kwargs, "reset", 64);

    const int32_t basic_t1 = 3;
    const int32_t basic_t2 = 7;
    const int32_t basic_t3 = 21;

    if (params.maximum_sample_value == 255 && near == 0) {
        params.threshold1 = value_or<int32_t>(kwargs, "t1", basic_t1);
        params.threshold2 = value_or<int32_t>(kwargs, "t2", basic_t2);
        params.threshold3 = value_or<int32_t>(kwargs, "t3", basic_t3);

        return params;
    }

    if (params.maximum_sample_value >= 128) {
        int32_t factor = (std::min(params.maximum_sample_value, 4095) + 128) / 256;
        params.threshold1 = value_or<int32_t>(kwargs, "t1", clamp(factor * (basic_t1 - 2) + 2 + 3 * near, near + 1, params.maximum_sample_value));
        params.threshold2 = value_or<int32_t>(kwargs, "t2", clamp(factor * (basic_t2 - 3) + 3 + 5 * near, params.threshold1, params.maximum_sample_value));
        params.threshold3 = value_or<int32_t>(kwargs, "t3", clamp(factor * (basic_t3 - 4) + 4 + 7 * near, params.threshold2, params.maximum_sample_value));

        return params;
    }

    int32_t factor = 256 / (params.maximum_sample_value + 1);
    params.threshold1 = value_or<int32_t>(kwargs, "t1", clamp(std::max(2, basic_t1 / factor + 3 * near), near + 1, params.maximum_sample_value));
    params.threshold2 = value_or<int32_t>(kwargs, "t2", clamp(std::max(3, basic_t2 / factor + 5 * near), params.threshold1, params.maximum_sample_value));
    params.threshold3 = value_or<int32_t>(kwargs, "t3", clamp(std::max(4, basic_t3 / factor + 7 * near), params.threshold2, params.maximum_sample_value));

    return params;
}

std::vector<uint8_t> interleaved_to_planar(const uint8_t *pBegin, const charls::frame_info &frame_info) {
    uint32_t samples_per_component = frame_info.width * frame_info.height;
    uint32_t bytes_per_sample = (frame_info.bits_per_sample + 7) / 8;
    std::vector<uint8_t> dest_buffer(frame_info.component_count * samples_per_component * bytes_per_sample);

    for (size_t j = 0; j < static_cast<size_t>(frame_info.component_count); ++j) {
        size_t component_offset = j * samples_per_component;
        for (size_t i = 0; i < samples_per_component; ++i) {
            dest_buffer[component_offset + i] = pBegin[i * frame_info.component_count + j];
        }
    }
    return dest_buffer;
}

PYBIND11_MODULE(_pycharls, module) {
    module.doc() = "Python bindings for CharLS using pybind11";
    py::class_<charls::frame_info>(module, "FrameInfo")
        .def(py::init())
        .def_readwrite("width", &charls::frame_info::width)
        .def_readwrite("height", &charls::frame_info::height)
        .def_readwrite("bits_per_sample", &charls::frame_info::bits_per_sample)
        .def_readwrite("component_count", &charls::frame_info::component_count);

    module.def(
        "encode",
        [](const py::buffer &src_buffer, const charls::frame_info &frame_info, const py::dict &kwargs) {
            charls::jpegls_encoder encoder;

            encoder.frame_info(frame_info);
            auto ilv = frame_info.component_count == 1 ? charls::interleave_mode::none : interleave_mode(kwargs);
            encoder.interleave_mode(ilv);
            auto near = value_or<int32_t>(kwargs, "near_lossless", 0);
            encoder.near_lossless(near);
            encoder.preset_coding_parameters(preset_coding_parameters(kwargs, frame_info.bits_per_sample, near));

            std::vector<uint8_t> dest(encoder.estimated_destination_size() * 2);
            encoder.destination(dest);

            auto src_buffer_info = src_buffer.request();
            if (ilv == charls::interleave_mode::none && frame_info.component_count > 1) {
                std::vector<uint8_t> src =
                    interleaved_to_planar(static_cast<const uint8_t *>(src_buffer_info.ptr), frame_info);
                const auto bytes_encoded = encoder.encode(src);
                dest.resize(bytes_encoded);
                return dest;
            }

            auto bytes_encoded = encoder.encode(src_buffer_info.ptr, src_buffer_info.size);
            dest.resize(bytes_encoded);
            return dest;
        },
        "encode a buffer to JPEG-LS");

    module.def("read_header",
        [](const py::buffer & src_buffer) {
            charls::jpegls_decoder decoder;
            auto src_buffer_info = src_buffer.request();
            decoder.source(src_buffer_info.ptr, src_buffer_info.size);
            bool spiff_header_present{};
            auto header = decoder.read_spiff_header(spiff_header_present);
            if (!spiff_header_present) {
                decoder.read_header();
                auto frame_info = decoder.frame_info();
                return py::dict(
                    "component_count"_a=frame_info.component_count,
                    "height"_a=frame_info.height,
                    "width"_a=frame_info.width,
                    "bits_per_sample"_a=frame_info.bits_per_sample
                );
            }

            return py::dict(
                "profile_id"_a=static_cast<int32_t>(header.profile_id),
                "component_count"_a=header.component_count,
                "height"_a=header.height,
                "width"_a=header.width,
                "color_space"_a=static_cast<int32_t>(header.color_space),
                "bits_per_sample"_a=header.bits_per_sample,
                "compression_type"_a=static_cast<int32_t>(header.compression_type),
                "resolution_units"_a=static_cast<int32_t>(header.resolution_units),
                "vertical_resolution"_a=header.vertical_resolution,
                "horizontal_resolution"_a=header.horizontal_resolution
            );
        },
        "Read header info from a JPEG-LS stream");

    module.def("decode", [] (const py::buffer & src_buffer) {
        charls::jpegls_decoder decoder;
        auto src_buffer_info = src_buffer.request();
        decoder.source(src_buffer_info.ptr, src_buffer_info.size);
        decoder.read_header();
        auto interleave_mode = decoder.interleave_mode();
        auto params = decoder.preset_coding_parameters();

        py::bytes_ destination_buffer;
        destination_buffer.resize(decoder.destination_size());
        auto dest_buffer_info = destination_buffer.request();
        decoder.decode(dest_buffer_info.ptr, dest_buffer_info.size);

        return destination_buffer;
    }, "Decode a JPEG-LS stream");

}
