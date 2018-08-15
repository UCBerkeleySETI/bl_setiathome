#include <numeric>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;


double compute_stdev(py::array_t<double> input) {
    py::buffer_info buf = input.request();
    double *v = (double *) buf.ptr;

    double sum = 0.0;
    double sq_sum = 0.0;
    size_t X = buf.shape[0];
    for(size_t idx = 0; idx < X; idx++){
        sum += v[idx];
        sq_sum += v[idx] * v[idx];
    }

    double mean = sum / buf.shape[0];
    double stdev = std::sqrt(sq_sum / buf.shape[0] - mean * mean);
    return stdev;


}

void requant_8i_2u(py::array_t<char> input, py::array_t<unsigned char> output) {
    // Input array should have size 4x that of output array.
    // Output array has to be uint8

    // Setup pointers and buffers to access data in ndarray
    py::buffer_info buf = input.request();
    py::buffer_info bufo = output.request();
    auto *v   = (char *) buf.ptr;
    auto *vo  = (unsigned char *) bufo.ptr;

    // Compute STDEV for real and imag
    double sum_re = 0.0,  sum_im = 0.0;
    double sq_sum_re = 0.0,  sq_sum_im = 0.0;
    size_t X = buf.shape[0] / 2;
    for(size_t idx = 0; idx < X; idx++){
        sum_re += v[2*idx];
        sq_sum_re += v[2*idx] * v[2*idx];
        sum_im += v[2*idx];
        sq_sum_im += v[2*idx] * v[2*idx];
    }
    double mean_re = sum_re / X;
    double mean_im = sum_im / X;
    double stdev_re = std::sqrt(sq_sum_re / X - mean_re * mean_re);
    double stdev_im = std::sqrt(sq_sum_im / X - mean_im * mean_im);

    // Do 2-bit conversion
    for(size_t idx = 0; idx < buf.shape[0] / 4; idx++) {

        // We are going to add all 2-bits together into one 8-bit number
        // So break out each into indexes
        size_t idxr = 4*idx;
        size_t idxi = 4*idx + 1;
        size_t idxr2 = 4*idx + 2;
        size_t idxi2 = 4*idx + 3;
        //std::cout << v[idxr] << " " << v[idxi] << " ";

        // Real part
        if(v[idxr] <  -0.98159883*stdev_re) {
            vo[idx] += 0 * 64;
        } else if(v[idxr] < 0){
            vo[idx] += 1 * 64;
        } else if(v[idxr] < 0.98159883*stdev_re) {
            vo[idx] += 2 * 64;
        } else {
            vo[idx] += 3 * 64;
        }

        if(v[idxr2] <  -0.98159883*stdev_re) {
            vo[idx] += 0 * 4;
        } else if(v[idxr2] < 0){
            vo[idx] += 1 * 4;
        } else if(v[idxr2] < 0.98159883*stdev_re) {
            vo[idx] += 2 * 4;
        } else {
            vo[idx] += 3 * 4;
        }

        // Imag part
        if(v[idxi] <  -0.98159883*stdev_im) {
            vo[idx] += 0 * 16;
        } else if(v[idxi] < 0) {
            vo[idx] += 1 * 16;
        } else if(v[idxi] < 0.98159883*stdev_im) {
            vo[idx] += 2 * 16;
        } else {
            vo[idx] += 3 * 16;
        }

        if(v[idxi2] <  -0.98159883*stdev_im) {
            vo[idx] += 0;
        } else if(v[idxi2] < 0) {
            vo[idx] += 1;
        } else if(v[idxi2] < 0.98159883*stdev_im) {
            vo[idx] += 2;
        } else {
            vo[idx] += 3;
        }

    }

}


PYBIND11_MODULE(requant_utils, m) {
    m.doc() = R"pbdoc(
        Pybind11 example plugin
        -----------------------

        .. currentmodule:: python_example

        .. autosummary::
           :toctree: _generate

           add
           subtract
    )pbdoc";

    m.def("compute_stdev", &compute_stdev, "Compute STDEV");

    m.def("requant_8i_2u", &requant_8i_2u, "Requantize 8bit signed integers [-128, 127] to 2-bit unsigned");

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
