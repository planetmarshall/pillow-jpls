#include <charls/charls.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <fmt/format.h>
#include <vector>

namespace py = pybind11;

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

charls::jpegls_pc_parameters preset_coding_parameters(const py::dict & kwargs) {
    charls::jpegls_pc_parameters params;
    params.maximum_sample_value = value_or<int32_t>(kwargs, "maxval", 0);
    params.threshold1 = value_or<int32_t>(kwargs, "t1", 0);
    params.threshold2 = value_or<int32_t>(kwargs, "t2", 0);
    params.threshold3 = value_or<int32_t>(kwargs, "t3", 0);
    params.reset_value = value_or<int32_t>(kwargs, "reset", 0);

    return params;
}

std::vector<uint8_t> interleaved_to_planar(const uint8_t *pBegin, const charls::frame_info &frame_info) {
    uint32_t samples_per_component = frame_info.width * frame_info.height;
    uint32_t bytes_per_sample = (frame_info.bits_per_sample + 7) / 8;
    std::vector<uint8_t> dest_buffer(frame_info.component_count * samples_per_component * bytes_per_sample);

    for (size_t j = 0; j < frame_info.component_count; ++j) {
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
            auto ilv = interleave_mode(kwargs);
            encoder.interleave_mode(ilv);
            encoder.near_lossless(value_or<int32_t>(kwargs, "near_lossless", 0));
            encoder.preset_coding_parameters(preset_coding_parameters(kwargs));

            std::vector<uint8_t> dest(encoder.estimated_destination_size());
            encoder.destination(dest);

            auto src_buffer_info = src_buffer.request();
            if (ilv == charls::interleave_mode::none) {
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
}
