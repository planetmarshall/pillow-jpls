#include <charls/charls.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <fmt/format.h>
#include <Eigen/Core>

#include <vector>
#include <variant>

namespace py = pybind11;
using namespace py::literals;
using Mx = Eigen::Array<uint8_t, Eigen::Dynamic, Eigen::Dynamic>;
using Map = Eigen::Map<Mx>;

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
    if (kwargs.contains(key)) {
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

    py::enum_<charls::spiff_profile_id>(module, "SpiffProfileId")
        .value("NotSpecified", charls::spiff_profile_id::none)
        .value("BiLevelFacsimile", charls::spiff_profile_id::bi_level_facsimile)
        .value("ContinuousToneBase", charls::spiff_profile_id::continuous_tone_base)
        .value("ContinuousToneFacsimile", charls::spiff_profile_id::continuous_tone_facsimile)
        .value("ContinuousToneProgressive", charls::spiff_profile_id::continuous_tone_progressive)
        .export_values();

    py::enum_<charls::spiff_color_space>(module, "SpiffColorSpace")
        .value("NotSpecified", charls::spiff_color_space::none)
        .value("BiLevelBlack", charls::spiff_color_space::bi_level_black)
        .value("BiLevelWhite", charls::spiff_color_space::bi_level_white)
        .value("CieLab", charls::spiff_color_space::cie_lab)
        .value("Cmy", charls::spiff_color_space::cmy)
        .value("Cmyk", charls::spiff_color_space::cmyk)
        .value("Grayscale", charls::spiff_color_space::grayscale)
        .value("PhotoYcc", charls::spiff_color_space::photo_ycc)
        .value("Rgb", charls::spiff_color_space::rgb)
        .value("YcbcrItuBt6011Rgb", charls::spiff_color_space::ycbcr_itu_bt_601_1_rgb)
        .value("YcbcrItuBt6011Video", charls::spiff_color_space::ycbcr_itu_bt_601_1_video)
        .value("YcbcrItuBt709Video", charls::spiff_color_space::ycbcr_itu_bt_709_video)
        .value("Ycck", charls::spiff_color_space::ycck)
        .export_values();

    py::enum_<charls::spiff_compression_type>(module, "SpiffCompressionType")
        .value("Uncompressed", charls::spiff_compression_type::uncompressed)
        .value("Jbig", charls::spiff_compression_type::jbig)
        .value("Jpeg", charls::spiff_compression_type::jpeg)
        .value("JpegLs", charls::spiff_compression_type::jpeg_ls)
        .value("ModifiedHuffman", charls::spiff_compression_type::modified_huffman)
        .value("ModifiedModifiedRead", charls::spiff_compression_type::modified_modified_read)
        .value("ModifiedRead", charls::spiff_compression_type::modified_read)
        .export_values();

    py::enum_<charls::spiff_resolution_units>(module, "SpiffResolutionUnits")
        .value("AspectRatio", charls::spiff_resolution_units::aspect_ratio)
        .value("DotsPerInch", charls::spiff_resolution_units::dots_per_inch)
        .value("DotsPerCentimeter", charls::spiff_resolution_units::dots_per_centimeter)
        .export_values();

    py::class_<charls::spiff_header>(module, "SpiffHeader", py::dynamic_attr())
        .def(py::init())
        .def_readwrite("horizontal_resolution", &charls::spiff_header::horizontal_resolution)
        .def_readwrite("vertical_resolution", &charls::spiff_header::vertical_resolution)
        .def_readwrite("resolution_units", &charls::spiff_header::resolution_units)
        .def_readwrite("compression_type", &charls::spiff_header::compression_type)
        .def_readwrite("bits_per_sample", &charls::spiff_header::bits_per_sample)
        .def_readwrite("color_space", &charls::spiff_header::color_space)
        .def_readwrite("width", &charls::spiff_header::width)
        .def_readwrite("height", &charls::spiff_header::height)
        .def_readwrite("component_count", &charls::spiff_header::component_count)
        .def_readwrite("profile_id", &charls::spiff_header::profile_id);

    module.def(
        "encode",
        [](const py::buffer &src_buffer, const charls::frame_info &frame_info, const std::optional<charls::spiff_header> & spiff, const py::kwargs &kwargs) {
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

          if (spiff) {
              encoder.write_spiff_header(*spiff);
          }
          auto bytes_encoded = encoder.encode(src_buffer_info.ptr, src_buffer_info.size);
            dest.resize(bytes_encoded);
            return dest;
        },
        "encode a buffer to JPEG-LS",
        py::arg("src_buffer"),
        py::arg("frame_info"),
        py::arg("spiff") = py::none()
        );

    module.def("read_header",
        [](const py::buffer & src_buffer) -> std::variant<charls::frame_info, charls::spiff_header> {
            charls::jpegls_decoder decoder;
            auto src_buffer_info = src_buffer.request();
            decoder.source(src_buffer_info.ptr, src_buffer_info.size);
            bool spiff_header_present{};
            auto header = decoder.read_spiff_header(spiff_header_present);
            if (!spiff_header_present) {
                decoder.read_header();
                return decoder.frame_info();
            }

            return header;
        },
        "Read header info from a JPEG-LS stream");

    module.def("decode", [] (const py::buffer & src_buffer) {
        charls::jpegls_decoder decoder;
        auto src_buffer_info = src_buffer.request();
        decoder.source(src_buffer_info.ptr, src_buffer_info.size);
        decoder.read_header();
        auto frame_info = decoder.frame_info();
        auto interleave_mode = decoder.interleave_mode();
        auto params = decoder.preset_coding_parameters();

        std::vector<uint8_t> destination_buffer;
        destination_buffer.resize(decoder.destination_size());

      if (interleave_mode == charls::interleave_mode::none && frame_info.component_count > 1) {
            std::vector<uint8_t> planar_buffer(decoder.destination_size());
            decoder.decode(planar_buffer);
            size_t elements_per_component = frame_info.width * frame_info.height;
            Map dest_view(static_cast<uint8_t *>(destination_buffer.data()), frame_info.component_count, elements_per_component);
            Map src_view(planar_buffer.data(), elements_per_component, frame_info.component_count);

            dest_view = src_view.transpose();
            return destination_buffer;
        }

        decoder.decode(destination_buffer);
        return destination_buffer;
    }, "Decode a JPEG-LS stream");

}
