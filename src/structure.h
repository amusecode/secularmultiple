#include "types.h"
extern "C"
{
int determine_binary_parents_and_levels(ParticlesMap *particlesMap, int *N_bodies, int *N_binaries, int *N_root_finding, int *N_ODE_equations);
void set_binary_masses_from_body_masses(ParticlesMap *particlesMap);
void set_positions_and_velocities(ParticlesMap *particlesMap);
void update_masses_positions_and_velocities_of_all_binaries(ParticlesMap *particlesMap);
void update_orbital_vectors_in_binaries_from_positions_and_velocities(ParticlesMap *particlesMap);

}
