/* SecularMultiple */
/* Adrian Hamers November 2019 */

#include "evolve.h"
#include "tools.h"

extern "C"
{

double compute_orbital_period(Particle *particle)
{
	double a = particle->a;
	double total_mass = particle->child1_mass_plus_child2_mass;
	return 2.0*M_PI*sqrt(a*a*a/(CONST_G*total_mass));
}

int sample_from_3d_maxwellian_distribution(double sigma, double v[3])
{
    double u1,u2,s,theta;
    for (int k=1; k<3; k++)
    {
        u1 = ((double) rand() / (RAND_MAX));
        u2 = ((double) rand() / (RAND_MAX));
        s = sigma*sqrt(-2.0*log(1.0 - u1));
        theta = 2.0*M_PI*u2;
        v[2*k-2] = s*cos(theta);
        v[2*k-1] = s*sin(theta);
    }    

    return 0;
}

double sample_from_y_times_maxwellian_distribution(double sigma)
{
    /* Sample random variable y from a distribution dN/dy \propto y*Exp[-y^2/(2 sigma^2)] */
    
    double x = ((double) rand() / (RAND_MAX));
    double y = sigma*sqrt( -2.0*log(1.0 - x) );
    
    return y;

}

int sample_spherical_coordinates_unit_vectors_from_isotropic_distribution(double r_hat_vec[3], double theta_hat_vec[3], double phi_hat_vec[3])
{
    double x1 = ((double) rand() / (RAND_MAX));
    double x2 = ((double) rand() / (RAND_MAX));    
    double theta = acos( 2.0*x1 - 1.0 ); /* inclination */
    double phi = 2.0*M_PI*x2; /* azimuthal angle */
    
    double cos_theta = cos(theta);
    double sin_theta = sin(theta);
    double cos_phi = cos(phi);
    double sin_phi = sin(phi);

    r_hat_vec[0] = sin_theta*cos_phi;
    r_hat_vec[1] = sin_theta*sin_phi;
    r_hat_vec[2] = cos_theta;
    
    theta_hat_vec[0] = cos_theta*cos_phi;
    theta_hat_vec[1] = cos_theta*sin_phi;
    theta_hat_vec[2] = -sin_theta;
    
    phi_hat_vec[0] = -sin_phi;
    phi_hat_vec[1] = cos_phi;
    phi_hat_vec[2] = 0.0;
    
    return 0;
}

double sample_from_power_law_distribution(double alpha, double y_lower, double y_upper)
{
    /* Sample random variable y from dN/dy ~ y^y_\alpha */

    double x = ((double) rand() / (RAND_MAX));
    double y;
    if (alpha == -1.0)
    {
        y = y_lower*pow(y_upper/y_lower,x);
    }
    else
    {
        y = pow( x*(pow(y_upper,alpha+1.0) - pow(y_lower,alpha+1.0)) + pow(y_lower,alpha+1.0), 1.0/( alpha + 1.0) );
    }
    
    return y;

}


/**********************************************
/* orbital element/vector conversion routines *
 **********************************************/
int compute_h_tot_vector(ParticlesMap* particlesMap, double h_tot_vec[3])
{
    for (int i=0; i<3; i++)
    {
        h_tot_vec[i] = 0.0;
    }
    
    ParticlesMapIterator it_p;
    for (it_p = particlesMap->begin(); it_p != particlesMap->end(); it_p++)
    {
        Particle *p = (*it_p).second;
        if (p->is_binary == 1)
        {
            for (int i=0; i<3; i++)
            {
                h_tot_vec[i] += p->h_vec[i];
            }
        }
    }
    
    return 0;
//    printf("compute_h_tot_vector %g %g %g\n",h_tot_vec[0],h_tot_vec[1],h_tot_vec[2]);
}
    
int compute_orbital_vectors_from_orbital_elements(double child1_mass, double child2_mass, double semimajor_axis, double eccentricity, double inclination, double argument_of_pericenter,double longitude_of_ascending_node, double *e_vec_x, double *e_vec_y, double *e_vec_z, double *h_vec_x, double *h_vec_y, double *h_vec_z)
{
    double cos_INCL = cos(inclination);
    double sin_INCL = sin(inclination);
    double cos_AP = cos(argument_of_pericenter);
    double sin_AP = sin(argument_of_pericenter);
    double cos_LAN = cos(longitude_of_ascending_node);
    double sin_LAN = sin(longitude_of_ascending_node);
           
    double h = (child1_mass*child2_mass*sqrt(CONST_G*semimajor_axis/(child1_mass+child2_mass)))*sqrt(1.0 - eccentricity*eccentricity);

    if (eccentricity==0.0)
    {
        /* The eccentricity cannot be exactly zero because the ODE solver computes e unit vectors */
        eccentricity = epsilon;
    }

    *e_vec_x = eccentricity*(cos_LAN*cos_AP - sin_LAN*sin_AP*cos_INCL);
    *e_vec_y = eccentricity*(sin_LAN*cos_AP + cos_LAN*sin_AP*cos_INCL);
    *e_vec_z = eccentricity*(sin_AP*sin_INCL);
    
    *h_vec_x = h*sin_LAN*sin_INCL;
    *h_vec_y = -h*cos_LAN*sin_INCL;
    *h_vec_z = h*cos_INCL;

    return 0;
}

int compute_orbital_vectors_from_orbital_elements_unit(double inclination, double argument_of_pericenter,double longitude_of_ascending_node, double *e_hat_vec_x, double *e_hat_vec_y, double *e_hat_vec_z, double *h_hat_vec_x, double *h_hat_vec_y, double *h_hat_vec_z)
{
    double cos_INCL = cos(inclination);
    double sin_INCL = sin(inclination);
    double cos_AP = cos(argument_of_pericenter);
    double sin_AP = sin(argument_of_pericenter);
    double cos_LAN = cos(longitude_of_ascending_node);
    double sin_LAN = sin(longitude_of_ascending_node);
           
    *e_hat_vec_x = (cos_LAN*cos_AP - sin_LAN*sin_AP*cos_INCL);
    *e_hat_vec_y = (sin_LAN*cos_AP + cos_LAN*sin_AP*cos_INCL);
    *e_hat_vec_z = (sin_AP*sin_INCL);
    
    *h_hat_vec_x = sin_LAN*sin_INCL;
    *h_hat_vec_y = -cos_LAN*sin_INCL;
    *h_hat_vec_z = cos_INCL;

    return 0;
}

int compute_orbital_elements_from_orbital_vectors(double child1_mass, double child2_mass, double h_tot_vec[3], double e_vec_x, double e_vec_y, double e_vec_z, double h_vec_x, double h_vec_y, double h_vec_z, double *semimajor_axis, double *eccentricity, double *inclination, double *argument_of_pericenter,double *longitude_of_ascending_node)
{
    double e_vec[3] = {e_vec_x,e_vec_y,e_vec_z};
    double h_vec[3] = {h_vec_x,h_vec_y,h_vec_z};
    double eccentricity_squared = norm3_squared(e_vec);
    *eccentricity = sqrt(eccentricity_squared);
    if (*eccentricity==0.0)
    {
        *eccentricity = epsilon;
    }
    double h_squared = norm3_squared(h_vec);
    *semimajor_axis = h_squared*(child1_mass+child2_mass)/( CONST_G*child1_mass*child1_mass*child2_mass*child2_mass*(1.0 - eccentricity_squared) );
    double h = sqrt(h_squared);
    
//    double x_vec[3] = {1.0,0.0,0.0};
//    double y_vec[3] = {0.0,1.0,0.0};
//    double z_vec[3] = {0.0,0.0,1.0};

    double h_tot = norm3(h_tot_vec);
//    printf("h_tot %g x %g y %g z %g\n",h_tot,h_tot_vec[0],h_tot_vec[1],h_tot_vec[2]);
    double x_vec[3], y_vec[3], z_vec[3];
    for (int i=0; i<3; i++)
    {
        z_vec[i] = h_tot_vec[i]/h_tot;
    }

//    printf("test %g %g %g\n",z_vec[0],z_vec[1],z_vec[2]);
    z_vec[0] = 0.0;
    z_vec[1] = 0.0;
    z_vec[2] = 1.0;

    /* the above assumes that the total angular momentum vector does not change (i.e. no SNe effects etc.) */
    
    double f = 1.0/sqrt( z_vec[0]*z_vec[0] + z_vec[2]*z_vec[2] );
    x_vec[0] = z_vec[2]*f;
    x_vec[1] = 0.0;
    x_vec[2] = -z_vec[0]*f;
    cross3(z_vec,x_vec,y_vec);

    double cos_INCL = dot3(h_vec,z_vec)/h;
    if (cos_INCL >= 1.0)
    {
        cos_INCL = 1.0 - epsilon;
    }
    if (cos_INCL <= -1.0)
    {
        cos_INCL = -1.0 + epsilon;
    }

    double LAN_vec[3],LAN_vec_unit[3];
    cross3(z_vec,h_vec,LAN_vec);
    double LAN_vec_norm = norm3(LAN_vec);
    if (LAN_vec_norm==0.0)
    {
        LAN_vec_norm = 1.0;
    }

    double e_vec_unit[3],h_vec_unit[3];

    for (int i=0; i<3; i++)
    {
        LAN_vec_unit[i] = LAN_vec[i]/LAN_vec_norm;
        e_vec_unit[i] = e_vec[i]/(*eccentricity);
        h_vec_unit[i] = h_vec[i]/h;
    }

    double sin_LAN = dot3(LAN_vec_unit,y_vec);
    double cos_LAN = dot3(LAN_vec_unit,x_vec);

    double e_vec_unit_cross_h_vec_unit[3];
    cross3(e_vec_unit,h_vec_unit,e_vec_unit_cross_h_vec_unit);
    double sin_AP = dot3(LAN_vec_unit,e_vec_unit_cross_h_vec_unit);
    double cos_AP = dot3(LAN_vec_unit,e_vec_unit);

    *inclination = acos(cos_INCL);
    *argument_of_pericenter = atan2(sin_AP,cos_AP);
    *longitude_of_ascending_node = atan2(sin_LAN,cos_LAN);
    
    return 0;
}

int get_inclination_relative_to_parent(int index, double *inclination_relative_to_parent)
{

    if (index > highest_particle_index)
    {
        return -1;
    }
  
    Particle * p = particlesMap[index];
    if (p->is_binary == false)
    {
        *inclination_relative_to_parent = 0.0;
        return 0;
    }
    if (p->parent == -1)
    {
        *inclination_relative_to_parent = 0.0;
        return 0;
    }

    Particle *parent = particlesMap[p->parent];
    

    double *h1_vec = p->h_vec;
    double *h2_vec = parent->h_vec;

    double h1 = norm3(h1_vec);
    double h2 = norm3(h2_vec);
    
    *inclination_relative_to_parent = acos( dot3(h1_vec,h2_vec)/(h1*h2) );
    
    return 0;
}


void compute_eccentric_anomaly_from_mean_anomaly(double mean_anomaly, double eccentricity, double *cos_eccentric_anomaly, double *sin_eccentric_anomaly)
{
    double eccentric_anomaly;
    double eccentric_anomaly_next = mean_anomaly;
    double epsilon2 = 1e-10;
    double error = 2.0*epsilon2;
    int j = 0;
    while (error > epsilon2 || j < 15)
    {
        j += 1;
        eccentric_anomaly = eccentric_anomaly_next;
        eccentric_anomaly_next = eccentric_anomaly - (eccentric_anomaly - eccentricity*sin(eccentric_anomaly) - mean_anomaly)/(1.0 - eccentricity*cos(eccentric_anomaly));
        error = fabs(eccentric_anomaly_next - eccentric_anomaly);
    }
    *cos_eccentric_anomaly = cos(eccentric_anomaly);
    *sin_eccentric_anomaly = sin(eccentric_anomaly);
}

void compute_true_anomaly_from_eccentric_anomaly(double cos_eccentric_anomaly, double sin_eccentric_anomaly, double eccentricity, double *cos_true_anomaly, double *sin_true_anomaly)
{
    *cos_true_anomaly = (cos_eccentric_anomaly - eccentricity)/(1.0 - eccentricity*cos_eccentric_anomaly);
    *sin_true_anomaly = sqrt(1.0 - eccentricity*eccentricity)*sin_eccentric_anomaly/(1.0 - eccentricity*cos_eccentric_anomaly);
}

double compute_true_anomaly_from_mean_anomaly(double mean_anomaly, double eccentricity)
{
    double cos_eccentric_anomaly,sin_eccentric_anomaly;
    double cos_true_anomaly,sin_true_anomaly;
    
    compute_eccentric_anomaly_from_mean_anomaly(mean_anomaly,eccentricity,&cos_eccentric_anomaly,&sin_eccentric_anomaly);
    compute_true_anomaly_from_eccentric_anomaly(cos_eccentric_anomaly,sin_eccentric_anomaly,eccentricity,&cos_true_anomaly,&sin_true_anomaly);
    double true_anomaly = atan2(sin_true_anomaly,cos_true_anomaly);

    return true_anomaly;
}

double compute_mean_anomaly_from_true_anomaly(double true_anomaly, double eccentricity)
{
    double cos_true_anomaly = cos(true_anomaly);
    double sin_true_anomaly = sin(true_anomaly);
    double den = 1.0/( 1.0 + eccentricity*cos_true_anomaly );
    
    double sin_eccentric_anomaly = sqrt(1.0 - eccentricity*eccentricity)*sin_true_anomaly*den;
    double cos_eccentric_anomaly = (eccentricity + cos_true_anomaly)*den;
    double eccentric_anomaly = atan2(sin_eccentric_anomaly,cos_eccentric_anomaly);
    double mean_anomaly = eccentric_anomaly - eccentricity*sin_eccentric_anomaly;
    
    return mean_anomaly;
}

double sample_random_true_anomaly(double eccentricity)//,int seed)
{
    //srand(seed);
    double x = ((double) rand() / (RAND_MAX));
    //printf("x %g %g\n",x,(double) rand());
    double mean_anomaly = (2.0*x - 1.0)*M_PI;
    double true_anomaly = compute_true_anomaly_from_mean_anomaly(mean_anomaly,eccentricity);

    return true_anomaly;
}

void compute_true_anomaly_from_mean_anomaly_hyperbolic_orbit(double mean_anomaly, double eccentricity,double *cos_true_anomaly,double *sin_true_anomaly)
{
    double eccentric_anomaly;
    
    double fabs_mean_anomaly = fabs(mean_anomaly);
    double sign_mean_anomaly;

    sign_mean_anomaly = copysign( 1.0, mean_anomaly);
    
    double eccentric_anomaly_next;    
    
    if (fabs_mean_anomaly < 3.0*eccentricity)
    {
        double s1 = fabs_mean_anomaly/(eccentricity-1.0);
        double s2 = pow( 6.0*fabs_mean_anomaly, 1.0/3.0);
        eccentric_anomaly_next = sign_mean_anomaly*min(s1,s2);
    }
    else
    {
        eccentric_anomaly_next = sign_mean_anomaly*log(1.0 + 2.0*fabs_mean_anomaly/eccentricity);
    }
    
    double epsilon = 1e-10;
    double error = 2.0*epsilon; /* to start: anything larger than epsilon */
    int j = 0;
    while (error > epsilon)
    {
        j += 1;
        eccentric_anomaly = eccentric_anomaly_next;
        eccentric_anomaly_next = eccentric_anomaly + (eccentric_anomaly - eccentricity*sinh(eccentric_anomaly) + mean_anomaly)/(eccentricity*cosh(eccentric_anomaly) - 1.0);
        error = fabs(eccentric_anomaly_next - eccentric_anomaly);
        
        if (j > 15)
        {
            //printf("test %d %g %g %g %g %g\n",j,mean_anomaly,eccentric_anomaly,eccentric_anomaly_next,error,epsilon);
            break;
        }
    }
    
    double tau = sqrt( (eccentricity+1.0)/(eccentricity-1.0) )*tanh(0.5*eccentric_anomaly); /* tan(true_anomaly/2) */
    double tau_sq = tau*tau;
    double temp = 1.0/(1.0 + tau_sq);
    
    *cos_true_anomaly = (1.0 - tau_sq)*temp;
    *sin_true_anomaly = 2.0*tau*temp;
    
    //printf("test %g %g\n",mean_anomaly,eccentric_anomaly);
}

void from_orbital_vectors_to_cartesian(double child1_mass, double child2_mass, double e_vec[3], double h_vec[3], double true_anomaly, double r[3], double v[3])
{
    double total_mass = child1_mass + child2_mass;
    
    double e = norm3(e_vec);
    double h = norm3(h_vec);

    if (e==0.0)
    {
        e = epsilon;
    }

    double e_vec_unit[3],q_vec_unit[3],q_vec[3];
    cross3(h_vec,e_vec,q_vec);
    double q = norm3(q_vec);

    int i;
    for (i=0; i<3; i++)
    {        
        e_vec_unit[i] = e_vec[i]/e;
        q_vec_unit[i] = q_vec[i]/q;        
    }
    
    double e_p2 = e*e;
    double j_p2 = 1.0 - e_p2;
   
    double a = h*h*total_mass/( CONST_G*child1_mass*child2_mass*child1_mass*child2_mass*j_p2 );

    double cos_f = cos(true_anomaly);
    double sin_f = sin(true_anomaly);
    
    double r_norm = a*j_p2/(1.0 + e*cos_f);
    double v_norm = sqrt( CONST_G*total_mass/(a*j_p2) );
    
    for (i=0; i<3; i++)
    {
        r[i] = r_norm*( cos_f*e_vec_unit[i] + sin_f*q_vec_unit[i]);
        v[i] = v_norm*( -sin_f*e_vec_unit[i] + (e + cos_f)*q_vec_unit[i] );
            
        #ifdef DEBUG
        printf("tools.cpp -- from_orbital_vectors_to_cartesian -- i %d r[i] %g v[i] %g\n",i,r[i],v[i]);
        #endif
    }
}

void from_cartesian_to_orbital_vectors(double child1_mass, double child2_mass, double r[3], double v[3], double e_vec[3], double h_vec[3], double *true_anomaly)
{
    double total_mass = child1_mass + child2_mass;
       
    double v_dot_v = dot3(v,v);
    double r_dot_v = dot3(r,v);
    double r_norm = norm3(r);
    for (int i=0; i<3; i++)
    {
        e_vec[i] = (r[i]*v_dot_v - v[i]*r_dot_v)/(CONST_G*total_mass) - r[i]/r_norm;
    }

    double mu = child1_mass*child2_mass/total_mass;
    cross3(r,v,h_vec);
    for (int i=0; i<3; i++)
    {
        h_vec[i] *= mu;
    }
    
    double e_vec_unit[3],h_vec_unit[3],q_vec_unit[3];
    double h = norm3(h_vec);
    double e = norm3(e_vec);
    if (e==0.0)
    {
        e = epsilon;
    }
    for (int i=0; i<3; i++)
    {
        h_vec_unit[i] = h_vec[i]/h;
        e_vec_unit[i] = e_vec[i]/e;
    }
    cross3(h_vec_unit,e_vec_unit,q_vec_unit);
    
    double cos_TA = dot3(r,e_vec_unit)/r_norm;
    double sin_TA = dot3(r,q_vec_unit)/r_norm;
    *true_anomaly = atan2( sin_TA, cos_TA );
    
    #ifdef DEBUG
    printf("tools.cpp -- from_cartesian_to_orbital_vectors -- e_vec %g %g %g h_vec %g %g %g TA %g\n",e_vec[0],e_vec[1],e_vec[2],h_vec[0],h_vec[1],h_vec[2],*true_anomaly);
    #endif
}

void get_position_and_velocity_vectors_from_particle(Particle *p, double r[3], double v[3])
{
    r[0] = p->X;
    r[1] = p->Y;
    r[2] = p->Z;
    v[0] = p->VX;
    v[1] = p->VY;
    v[2] = p->VZ;
}
void set_position_and_velocity_vectors_in_particle(Particle *p,  double r[3], double v[3])
{
    p->X = r[0];
    p->Y = r[1];
    p->Z = r[2];
    p->VX = v[0];
    p->VY = v[1];
    p->VZ = v[2];
}

}
