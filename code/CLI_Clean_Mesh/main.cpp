#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
#include <CGAL/Polygon_mesh_processing/IO/polygon_mesh_io.h>
#include <CGAL/Polygon_mesh_processing/self_intersections.h>
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
typedef boost::graph_traits<Surface_mesh>::face_descriptor          face_descriptor;

namespace PMP = CGAL::Polygon_mesh_processing;

int main(int argc, char *argv[])
{
    const std::string filename = (argc > 1) ? argv[1] : CGAL::data_file_path("data/IGN/results/BATIMENT0000000320899175.obj");
    const char *outfilename = (argc > 2) ? argv[2] : "BATIMENT0000000320899175.obj";

    Surface_mesh mesh;

    if (!PMP::IO::read_polygon_mesh(filename, mesh))
    {
        std::cerr << "Invalid input." << std::endl;
        return 1;
    }

    std::vector<Point> _points;
    std::vector<std::vector<std::size_t>> _polygons;

    PMP::polygon_mesh_to_polygon_soup(mesh, _points, _polygons);
    std::cout << _points.size() << " points loaded" << std::endl;
    std::cout << _polygons.size() << " polygons loaded" << std::endl;

    int count = PMP::merge_duplicate_points_in_polygon_soup(_points,_polygons);
    std::cout << count << " duplicate points removed" << std::endl;

    count = PMP::merge_duplicate_polygons_in_polygon_soup(_points,_polygons);
    std::cout << count << " duplicate polygons removed" << std::endl;

    PMP::repair_polygon_soup(_points, _polygons,CGAL::parameters::erase_all_duplicates(true).require_same_orientation(true));
    std::cout << _points.size() << " points after repairs" << std::endl;
    std::cout << _polygons.size() << " polygons after repairs" << std::endl;

    // Check for self intersection
    bool intersecting = PMP::does_self_intersect<CGAL::Parallel_if_available_tag>(mesh, CGAL::parameters::vertex_point_map(get(CGAL::vertex_point, mesh)));
    std::cout << (intersecting ? "There are self-intersections." : "There is no self-intersection.") << std::endl;
    std::vector<std::pair<face_descriptor, face_descriptor> > intersected_tris;
    PMP::self_intersections<CGAL::Parallel_if_available_tag>(faces(mesh), mesh, std::back_inserter(intersected_tris));
    std::cout << intersected_tris.size() << " pairs of triangles intersect." << std::endl;
    // std::cout << intersected_tris << std::endl;

    const bool success = PMP::orient_polygon_soup(_points, _polygons);
    std::cout << success << " orient result" << std::endl;

    // PMP::orient_to_bound_a_volume(mesh);

    PMP::polygon_soup_to_polygon_mesh(_points, _polygons, mesh);

    PMP::triangulate_faces(mesh);

    // if (CGAL::is_closed(mesh))
    // {
    //     std::cout << "The obtained mesh is closed" << std::endl;
    //     PMP::orient_to_bound_a_volume(mesh);
    // } else
    // {
    //     std::cout << filename << std::endl;
    // }

    // Confirm that all faces are triangles.
    // for (boost::graph_traits<Surface_mesh>::face_descriptor f : faces(mesh))
    //     if (!CGAL::is_triangle(halfedge(f, mesh), mesh))
    //         std::cerr << "Error: non-triangular face left in mesh." << std::endl;

    CGAL::IO::write_polygon_mesh(outfilename, mesh, CGAL::parameters::stream_precision(17));

    return 0;
}