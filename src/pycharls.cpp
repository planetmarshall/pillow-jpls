#include <charls/charls.h>
#include <pybind11/pybind11.h>

#include <pybind11/stl.h>

namespace py = pybind11;

std::vector<uint8_t> sample_interleave_to_planar(const uint8_t * pBegin, const charls::frame_info & frame_info) {
  uint32_t samples_per_component = frame_info.width * frame_info.height;
  uint32_t bytes_per_sample = (frame_info.bits_per_sample + 7) / 8;
  std::vector<uint8_t> planar_buffer(frame_info.component_count * samples_per_component * bytes_per_sample);

  for (size_t j = 0; j < frame_info.component_count; ++j) {
    size_t component_offset = j * samples_per_component;
    for (size_t i = 0; i < samples_per_component; ++i) {
      planar_buffer[component_offset + i] = pBegin[i * frame_info.component_count + j];
    }
  }

  return planar_buffer;
}

PYBIND11_MODULE(_pycharls, module) {
  module.doc() = "Python bindings for CharLS using pybind11";
  py::class_<charls::frame_info>(module, "FrameInfo")
      .def(py::init())
      .def_readwrite("width", &charls::frame_info::width)
      .def_readwrite("height", &charls::frame_info::height)
      .def_readwrite("bits_per_sample", &charls::frame_info::bits_per_sample)
      .def_readwrite("component_count", &charls::frame_info::component_count);

  module.def("encode_from_interleaved_samples", []( const py::buffer & src_buffer, const charls::frame_info & frame_info) {
    charls::jpegls_encoder encoder;
    encoder.frame_info(frame_info);
    std::vector<uint8_t> dest(encoder.estimated_destination_size());
    auto src_buffer_info = src_buffer.request();
    std::vector<uint8_t> src = sample_interleave_to_planar(static_cast<const uint8_t * >(src_buffer_info.ptr), frame_info);
    encoder.destination(dest);
    const auto bytes_encoded = encoder.encode(src);
    dest.resize(bytes_encoded);

    return dest;
  },
  "encode a buffer to JPEG-LS"
  );
}


