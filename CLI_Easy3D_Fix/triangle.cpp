#include <easy3d/util/initializer.h>
#include <easy3d/algo/surface_mesh_polygonization.h>
#include <easy3d/algo/surface_mesh_triangulation.h>
#include <easy3d/core/surface_mesh.h>
#include <easy3d/fileio/surface_mesh_io.h>
#include <easy3d/util/resource.h>
#include <easy3d/algo_ext/surfacer.h>

using namespace easy3d;

int main(int argc, char** argv) {

    std::string input_result_file = (argc > 1) ? argv[1] : std::string(EASY3D_ROOT_DIR) + "/../data/IGN/results/Node_79.obj";
    std::string output_fixed_result_file = (argc > 2) ? argv[2] : std::string(EASY3D_ROOT_DIR) + "/../data/IGN/results_fixed_with_easy3d/Node_79.obj";

    SurfaceMesh* mesh = SurfaceMeshIO::load(input_result_file);
    if (!mesh) {
        LOG(ERROR) << "Error: failed to load model. Please make sure the file exists and format is correct.";
        return EXIT_FAILURE;
    }

    // STEP 1 : Repair polygon soup

    Surfacer::repair_polygon_soup(mesh);
    std::cout << "repair done" << std::endl;

    // STEP 2 : Triangulate

    SurfaceMeshTriangulation triangulator(mesh);
    triangulator.triangulate(SurfaceMeshTriangulation::MIN_AREA);
    std::cout << "triangulate done" << std::endl;

    // STEP 2: Polygonization as implemented in Easy3D client

    // stitch first: to encourage large polygons
    Surfacer::stitch_borders(mesh);
    Surfacer::merge_reversible_connected_components(mesh);
    std::cout << "stitch/merge done" << std::endl;

    // polygonization
    SurfaceMeshPolygonization polygonizer;
    polygonizer.apply(mesh);
    std::cout << "polygonizer done" << std::endl;

    // stitch again (the "merge-edge" edge operation in polygonization may result in some borders)
    Surfacer::stitch_borders(mesh);
    Surfacer::merge_reversible_connected_components(mesh);
    std::cout << "stitch/merge done" << std::endl;

    if (SurfaceMeshIO::save(output_fixed_result_file, mesh))
        std::cout << "mesh saved to \'" << output_fixed_result_file << "\'"  << std::endl;
    else
        std::cerr << "failed create the new file" << std::endl;
 
    // delete the mesh (i.e., release memory)
    delete mesh;
 
    return EXIT_SUCCESS;

}
