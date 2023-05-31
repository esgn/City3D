#include <iostream>
#include <string>
#include <dirent.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/boost/graph/helpers.h>
#include <CGAL/Polygon_mesh_processing/IO/polygon_mesh_io.h>
#include <CGAL/Polygon_mesh_processing/polygon_mesh_to_polygon_soup.h>
#include <CGAL/Polygon_mesh_processing/polygon_soup_to_polygon_mesh.h>
#include <CGAL/Polygon_mesh_processing/stitch_borders.h>
#include <CGAL/Polygon_mesh_processing/border.h>
#include <CGAL/Polygon_mesh_processing/repair_polygon_soup.h>
#include <CGAL/Polygon_mesh_processing/repair.h>
#include <CGAL/Polygon_mesh_processing/manifoldness.h>
#include <CGAL/Polygon_mesh_processing/self_intersections.h>
#include <CGAL/Polygon_mesh_processing/triangulate_hole.h>
typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel;
typedef Kernel::Point_3 Point;
typedef CGAL::Surface_mesh<Point> Surface_mesh;
typedef boost::graph_traits<Surface_mesh>::vertex_descriptor vertex_descriptor;
typedef boost::graph_traits<Surface_mesh>::halfedge_descriptor halfedge_descriptor;
typedef boost::graph_traits<Surface_mesh>::face_descriptor face_descriptor;

namespace PMP = CGAL::Polygon_mesh_processing;
namespace NP = CGAL::parameters;

int main(int argc, const char **argv)
{

  struct dirent *entry = nullptr;
  DIR *dp = nullptr;

  std::string directory_name = (argc > 1) ? argv[1] : "results_remaining_faces_fixed";
  std::string directory = std::string(CITY3D_ROOT_DIR) + "/../data/IGN/" + directory_name;

  dp = opendir(directory.c_str());

  std::cout << "Testing content of " + directory << std::endl;

  int is_ok = 0;
  int is_nok = 0;
  int is_ok_after_repair = 0;
  int is_nok_after_repair = 0;
  int is_ok_after_stitching = 0;
  int is_nok_after_stitching = 0;
  int is_ok_after_hole_repairing = 0;
  int is_nok_after_hole_repairing =0;

  int ok_has_intersected_faces = 0;
  int nok_has_intersected_faces = 0;
  int ok_has_non_manifold_vertices = 0;
  int nok_has_non_manifold_vertices = 0;
  int ok_has_holes = 0;
  int nok_has_holes = 0;

  if (dp != nullptr)
  {

    while ((entry = readdir(dp)))
    {

      std::string filename = std::string(entry->d_name);
      if ((filename == ".") || (filename == ".."))
      {
        continue;
      }

      std::string filepath = directory + "/" + std::string(entry->d_name);

      Surface_mesh mesh;

      if (!PMP::IO::read_polygon_mesh(filepath, mesh))
      {
        std::cerr << "Invalid input." << std::endl;
        return 1;
      }

      if (CGAL::is_closed(mesh) && CGAL::is_valid(mesh))
      {
        is_ok += 1;
      }
      else
      {
        is_nok += 1;
      }

      if (!CGAL::is_closed(mesh) || !CGAL::is_valid(mesh))
      {
        std::vector<Point> _points;
        std::vector<std::vector<std::size_t>> _polygons;
        PMP::polygon_mesh_to_polygon_soup(mesh, _points, _polygons);
        PMP::repair_polygon_soup(_points, _polygons);
        PMP::orient_polygon_soup(_points, _polygons);
        PMP::polygon_soup_to_polygon_mesh(_points, _polygons, mesh);
      }

      if (CGAL::is_closed(mesh) && CGAL::is_valid(mesh))
      {
        is_ok_after_repair += 1;
      }
      else
      {
        is_nok_after_repair += 1;
      }

      // Try stitching
      if (!CGAL::is_closed(mesh) || !CGAL::is_valid(mesh))
      {
        PMP::stitch_borders(mesh);
      }

      if (CGAL::is_closed(mesh) && CGAL::is_valid(mesh))
      {
        is_ok_after_stitching += 1;
      }
      else
      {
        is_nok_after_stitching += 1;
        std::cout << filename + " is invalid" << std::endl;
      }

      // Check for self intersections in the mesh
      bool intersecting = PMP::does_self_intersect<CGAL::Parallel_if_available_tag>(mesh, CGAL::parameters::vertex_point_map(get(CGAL::vertex_point, mesh)));

      if (CGAL::is_closed(mesh) && CGAL::is_valid(mesh))
      {
        if (intersecting)
        {
          ok_has_intersected_faces += 1;
        }
      }
      else
      {
        if (intersecting)
        {
          nok_has_intersected_faces += 1;
        }
      }

      // Check for non manifold vertices
      int counter = 0;
      for (vertex_descriptor v : vertices(mesh))
      {
        if (PMP::is_non_manifold_vertex(v, mesh))
        {
          ++counter;
        }
      }

      if (CGAL::is_closed(mesh) && CGAL::is_valid(mesh))
      {
        if (counter > 0)
        {
          ok_has_non_manifold_vertices += 1;
        }
      }
      else
      {
        if (counter > 0)
        {
          nok_has_non_manifold_vertices += 1;
        }
      }

      // Check for holes

      unsigned int nb_holes = 0;
      std::vector<halfedge_descriptor> border_cycles;
      PMP::extract_boundary_cycles(mesh, std::back_inserter(border_cycles));

      for (halfedge_descriptor h : border_cycles)
      {
        ++nb_holes;
      }

      if (CGAL::is_closed(mesh) && CGAL::is_valid(mesh))
      {
        if (nb_holes > 0)
        {
          ok_has_holes += 1;
        }
      }
      else
      {
        if (nb_holes > 0)
        {
          nok_has_holes += 1;
        }
      }

      // Try and repair holes

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
        is_ok_after_hole_repairing += 1;
      }
      else
      {
        is_nok_after_hole_repairing += 1;
      }

    }

    std::cout << std::to_string(is_ok) + " valid and closed models" << std::endl;
    std::cout << std::to_string(is_nok) + " invalid or unclosed models" << std::endl;
    std::cout << "Trying CGAL polygon soup repair" << std::endl;
    std::cout << std::to_string(is_ok_after_repair) + " valid and closed models after polygon soup repair" << std::endl;
    std::cout << std::to_string(is_nok_after_repair) + " invalid or unclosed models after polygon soup repair" << std::endl;
    std::cout << "Trying CGAL stitching" << std::endl;
    std::cout << std::to_string(is_ok_after_stitching) + " valid and closed models after stitching" << std::endl;
    std::cout << std::to_string(is_nok_after_stitching) + " invalid or unclosed models after stitching" << std::endl;
    std::cout << "Checking for self intesecting faces" << std::endl;
    std::cout << std::to_string(ok_has_intersected_faces) + " valid and closed models with self intersecting faces" << std::endl;
    std::cout << std::to_string(nok_has_intersected_faces) + " invalid or unclosed models with self intersecting faces" << std::endl;
    std::cout << "Checking for non manifold vertices" << std::endl;
    std::cout << std::to_string(ok_has_non_manifold_vertices) + " valid and closed models with non manifold vertices" << std::endl;
    std::cout << std::to_string(nok_has_non_manifold_vertices) + " invalid or unclosed models with non manifold vertices" << std::endl;
    std::cout << "Checking for holes" << std::endl;
    std::cout << std::to_string(ok_has_holes) + " valid and closed models with holes" << std::endl;
    std::cout << std::to_string(nok_has_holes) + " invalid or unclosed models with holes" << std::endl;
    std::cout << "Trying hole repairing" << std::endl;
    std::cout << std::to_string(is_ok_after_hole_repairing) + " valid and closed models after holes repairing" << std::endl;
    std::cout << std::to_string(is_nok_after_hole_repairing) + " invalid or unclosed models after holes repairing" << std::endl;

    closedir(dp);
    return 0;
  }
}
