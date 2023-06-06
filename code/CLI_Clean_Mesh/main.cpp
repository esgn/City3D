#include <iostream>
#include <string>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/boost/graph/helpers.h>
#include <CGAL/boost/graph/iterator.h>
#include <CGAL/Polygon_mesh_processing/border.h>
#include <CGAL/Polygon_mesh_processing/corefinement.h>
#include <CGAL/Polygon_mesh_processing/IO/polygon_mesh_io.h>
#include <CGAL/Polygon_mesh_processing/internal/repair_extra.h>
#include <CGAL/Polygon_mesh_processing/internal/Corefinement/face_graph_utils.h>
#include <CGAL/Polygon_mesh_processing/internal/Corefinement/predicates.h>
#include <CGAL/Polygon_mesh_processing/manifoldness.h>
#include <CGAL/Polygon_mesh_processing/orientation.h>
#include <CGAL/Polygon_mesh_processing/orient_polygon_soup.h>
#include <CGAL/Polygon_mesh_processing/orient_polygon_soup_extension.h>
#include <CGAL/Polygon_mesh_processing/polygon_mesh_to_polygon_soup.h>
#include <CGAL/Polygon_mesh_processing/polygon_soup_to_polygon_mesh.h>
#include <CGAL/Polygon_mesh_processing/remesh.h>
#include <CGAL/Polygon_mesh_processing/repair_polygon_soup.h>
#include <CGAL/Polygon_mesh_processing/repair_self_intersections.h>
#include <CGAL/Polygon_mesh_processing/self_intersections.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
#include <CGAL/Polygon_mesh_processing/triangulate_hole.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel;
typedef Kernel::Point_3 Point;
typedef CGAL::Surface_mesh<Point> Surface_mesh;
typedef boost::graph_traits<Surface_mesh>::vertex_descriptor vertex_descriptor;
typedef boost::graph_traits<Surface_mesh>::halfedge_descriptor halfedge_descriptor;
typedef boost::graph_traits<Surface_mesh>::edge_descriptor edge_descriptor;
typedef boost::graph_traits<Surface_mesh>::face_descriptor face_descriptor;

namespace PMP = CGAL::Polygon_mesh_processing;
namespace NP = CGAL::parameters;

int main(int argc, char *argv[])
{
  // input parameters

  const std::string filepath = (argc > 1) ? argv[1] : CGAL::data_file_path("data/IGN/results_footprint_fixed/BATIMENT0000000037535513.obj");
  const char *outfilename = (argc > 2) ? argv[2] : "BATIMENT0000000037535513_cleaned.obj";
  const int output_interesecting_faces = (argc > 3) ? std::stoi(argv[3]) : 0;

  // simple scenario

  Surface_mesh mesh;

  if (!PMP::IO::read_polygon_mesh(filepath, mesh))
  {
    std::cerr << "Invalid input." << std::endl;
    return 1;
  }

  if (CGAL::is_closed(mesh) && CGAL::is_valid(mesh))
  {
    // orient the mesh
    PMP::orient(mesh);
    // triangulate model to check orientation
    Surface_mesh copy;
    CGAL::copy_face_graph(mesh, copy);
    PMP::triangulate_faces(copy);
    // reverse orientation in the original mesh if necessary
    if (!PMP::is_outward_oriented(copy))
    {
      PMP::reverse_face_orientations(mesh);
    }
    CGAL::IO::write_polygon_mesh(outfilename, mesh, CGAL::parameters::stream_precision(17));
    std::cout << "Mesh was directly valid and closed" << std::endl;
    return 0;
  }

  // Dealing with a faulty model from here

  // Polygon mesh to polygon soup and try repairing

  std::vector<Point> points;
  std::vector<std::vector<std::size_t>> polygons;
  PMP::polygon_mesh_to_polygon_soup(mesh, points, polygons);
  PMP::repair_polygon_soup(points, polygons);
  PMP::orient_polygon_soup(points, polygons);
  PMP::polygon_soup_to_polygon_mesh(points, polygons, mesh);

  if (CGAL::is_closed(mesh) && CGAL::is_valid(mesh))
  {
    // orient the mesh
    PMP::orient(mesh);
    // triangulate model to check orientation
    Surface_mesh copy;
    CGAL::copy_face_graph(mesh, copy);
    PMP::triangulate_faces(copy);
    // reverse orientation in the original mesh if necessary
    if (!PMP::is_outward_oriented(copy))
    {
      PMP::reverse_face_orientations(mesh);
    }
    CGAL::IO::write_polygon_mesh(outfilename, mesh, CGAL::parameters::stream_precision(17));
    std::cout << "Mesh was valid and closed after CGAL default repair" << std::endl;
    return 0;
  }

  // Try stitching

  PMP::stitch_borders(mesh);

  if (CGAL::is_closed(mesh) && CGAL::is_valid(mesh))
  {
    // orient the mesh
    PMP::orient(mesh);
    // triangulate model to check orientation
    Surface_mesh copy;
    CGAL::copy_face_graph(mesh, copy);
    PMP::triangulate_faces(copy);
    // reverse orientation in the original mesh if necessary
    if (!PMP::is_outward_oriented(copy))
    {
      PMP::reverse_face_orientations(mesh);
    }
    PMP::orient(mesh);
    CGAL::IO::write_polygon_mesh(outfilename, mesh, CGAL::parameters::stream_precision(17));
    std::cout << "Mesh was valid and closed after CGAL stitching" << std::endl;
    return 0;
  }

  // Try to fix holes

  unsigned int nb_holes = 0;
  std::vector<halfedge_descriptor> border_cycles;
  PMP::extract_boundary_cycles(mesh, std::back_inserter(border_cycles));

  if (!CGAL::is_closed(mesh) || !CGAL::is_valid(mesh))
  {
    for (halfedge_descriptor h : border_cycles)
    {
      std::vector<face_descriptor> patch_facets;
      std::vector<vertex_descriptor> patch_vertices;
      bool success = std::get<0>(PMP::triangulate_refine_and_fair_hole(mesh,
                                                                       h,
                                                                       std::back_inserter(patch_facets),
                                                                       std::back_inserter(patch_vertices)));
    }
  }

  if (CGAL::is_closed(mesh) && CGAL::is_valid(mesh))
  {
    // orient the mesh
    PMP::orient(mesh);
    // triangulate model to check orientation
    Surface_mesh copy;
    CGAL::copy_face_graph(mesh, copy);
    PMP::triangulate_faces(copy);
    // reverse orientation in the original mesh if necessary
    if (!PMP::is_outward_oriented(copy))
    {
      PMP::reverse_face_orientations(mesh);
    }
    CGAL::IO::write_polygon_mesh(outfilename, mesh, CGAL::parameters::stream_precision(17));
    std::cout << "Mesh was valid and closed after CGAL triangulate_refine_and_fair_hole()" << std::endl;
    return 0;
  }

  return 2;
}
