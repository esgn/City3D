#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
#include <CGAL/Polygon_mesh_processing/IO/polygon_mesh_io.h>
#include <CGAL/boost/graph/helpers.h>
#include <iostream>
#include <string>
#include <CGAL/Polygon_mesh_processing/polygon_mesh_to_polygon_soup.h>
#include <CGAL/Polygon_mesh_processing/polygon_soup_to_polygon_mesh.h>
#include <CGAL/Polygon_mesh_processing/orient_polygon_soup.h>
#include <CGAL/Polygon_mesh_processing/repair_polygon_soup.h>
#include <CGAL/Polygon_mesh_processing/orientation.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel;
typedef Kernel::Point_3 Point;
typedef CGAL::Surface_mesh<Point> Surface_mesh;
namespace PMP = CGAL::Polygon_mesh_processing;

int main(int argc, char *argv[])
{
    const std::string filename = (argc > 1) ? argv[1] : CGAL::data_file_path("BATIMENT0000000320898295.obj");
    const char *outfilename = (argc > 2) ? argv[2] : "BATIMENT0000000320898295_clean.obj";

    Surface_mesh mesh;

    if (!PMP::IO::read_polygon_mesh(filename, mesh))
    {
        std::cerr << "Invalid input." << std::endl;
        return 1;
    }

    std::vector<Point> _points;
    std::vector<std::vector<std::size_t>> _polygons;

    PMP::polygon_mesh_to_polygon_soup(mesh, _points, _polygons);
    PMP::repair_polygon_soup(_points, _polygons);
    PMP::orient_polygon_soup(_points, _polygons);
    PMP::polygon_soup_to_polygon_mesh(_points, _polygons, mesh);
    PMP::triangulate_faces(mesh);

    if (CGAL::is_closed(mesh))
    {
        std::cout << "The obtained mesh is closed" << std::endl;
        PMP::orient_to_bound_a_volume(mesh);
    } // Confirm that all faces are triangles.

    for (boost::graph_traits<Surface_mesh>::face_descriptor f : faces(mesh))
        if (!CGAL::is_triangle(halfedge(f, mesh), mesh))
            std::cerr << "Error: non-triangular face left in mesh." << std::endl;

    CGAL::IO::write_polygon_mesh(outfilename, mesh, CGAL::parameters::stream_precision(17));

    return 0;
}