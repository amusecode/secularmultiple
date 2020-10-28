import numpy as np
import argparse
import time
        
from secularmultiple import SecularMultiple,Particle,Tools

"""
Several routines for testing the code/installation. 
To run all tests, simply run `python test_secularmultiple.py'.
Specific tests can be run with the command line --t i, where i is the
number of the test. Use --verbose for verbose terminal output, and --plot to
make and show plots if applicable (required Matplotlib).

Adrian Hamers, March 2020
"""

try:
    from matplotlib import pyplot
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

def add_bool_arg(parser, name, default=False,help=None):
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--' + name, dest=name, action='store_true',help="Enable %s"%help)
    group.add_argument('--no-' + name, dest=name, action='store_false',help="Disable %s"%help)
    parser.set_defaults(**{name:default})

def parse_arguments():

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--t",                           type=int,     dest="test",                        default=0,              help="Test number")
    
    ### boolean arguments ###
    add_bool_arg(parser, 'verbose',                         default=False,         help="verbose terminal output")
    add_bool_arg(parser, 'plot',                            default=False,         help="make plots")
    
    args = parser.parse_args()

    return args

class test_secularmultiple():

    def test1(self,args):
        print("Basic test using reference system of Naoz et al. (2009)")

        particles = Tools.create_nested_multiple(3, [1.0,1.0e-3,40.0e-3],[6.0,100.0],[0.001,0.6],[0.0,65.0*np.pi/180.0],[45.0*np.pi/180.0,0.0],[0.0,0.0])
        binaries = [x for x in particles if x.is_binary==True]
        
        code = SecularMultiple()
        code.add_particles(particles)
        inner_binary = binaries[0]
        outer_binary = binaries[1]
        
        e_print = []
        INCL_print = []
        rel_INCL_print = []
        t_print = []
        
        start = time.time()
    
        t = 0.0
        N = 1000
        tend = 3.0e7

        dt = tend/float(N)
        while t<=tend:
            code.evolve_model(t)
            t+=dt
        
            if args.verbose==True:
                print( 't',t,'es',[x.e for x in binaries],'INCL_parent',inner_binary.INCL_parent)
                        
            rel_INCL_print.append(inner_binary.INCL_parent)
            e_print.append(inner_binary.e)
            INCL_print.append(inner_binary.INCL)
            t_print.append(t)
        
        if args.verbose==True:
            print('wall time',time.time()-start)
        
        t_print = np.array(t_print)
        rel_INCL_print = np.array(rel_INCL_print)
        e_print = np.array(e_print)

        assert round(e_print[-1],3) == 0.204
        assert round(rel_INCL_print[-1],3) == 1.217
        
        print("Test passed")

        code.reset()
                
        if HAS_MATPLOTLIB==True and args.plot==True:
            fig=pyplot.figure()
            plot1=fig.add_subplot(2,1,1)
            plot2=fig.add_subplot(2,1,2,yscale="log")
            plot1.plot(1.0e-6*t_print,rel_INCL_print*180.0/np.pi)
            plot2.plot(1.0e-6*t_print,1.0-e_print)
            plot2.set_xlabel("$t/\mathrm{Myr}$")
            plot1.set_ylabel("$i_\mathrm{rel}/\mathrm{deg}$")
            plot2.set_ylabel("$1-e_\mathrm{in}$")
            pyplot.show()

    def test2(self,args):
        print("Test 1PN precession in 2-body system")

        particles = Tools.create_nested_multiple(2,[1.0, 1.0], [1.0], [0.99], [0.01], [0.01], [0.01])
        binaries = [x for x in particles if x.is_binary == True]

        for b in binaries:
            b.include_pairwise_1PN_terms = True

        code = SecularMultiple()
        code.add_particles(particles)

        t = 0.0
        N=1000
        tend = 1.0e7
        dt=tend/float(N)

        t_print_array = []
        a_print_array = []
        e_print_array = []
        AP_print_array = []

        while (t<tend):
            t+=dt
            code.evolve_model(t)

            if args.verbose==True:
                print( 't/Myr',t,'omega',binaries[0].AP)
            t_print_array.append(t)
            a_print_array.append(binaries[0].a)
            e_print_array.append(binaries[0].e)
            AP_print_array.append(binaries[0].AP)
        
        t_print_array = np.array(t_print_array)
        a_print_array = np.array(a_print_array)
        e_print_array = np.array(e_print_array)
        AP_print_array = np.array(AP_print_array)
        
        CONST_G = code.CONST_G
        CONST_C = code.CONST_C

        # Theoretical prediction #
        a = binaries[0].a
        e = binaries[0].e
        M = binaries[0].mass
        rg = CONST_G*M/(CONST_C**2)
        P = 2.0*np.pi*np.sqrt(a**3/(CONST_G*M))
        t_1PN = (1.0/3.0)*P*(1.0-e**2)*(a/rg)

        AP = 0.01 +2.0*np.pi*tend/t_1PN
        AP = (AP+np.pi)%(2.0*np.pi) - np.pi ### -pi < AP < pi
        
        assert round(AP_print_array[-1],5) == round(AP,5)
        print("Test passed")

        code.reset()
                
        if HAS_MATPLOTLIB == True and args.plot==True:
            fig = pyplot.figure(figsize=(16,10))
            plot1 = fig.add_subplot(4,1,1)
            plot2 = fig.add_subplot(4,1,2,yscale="log")
            plot3 = fig.add_subplot(4,1,3,yscale="log")
            plot4 = fig.add_subplot(4,1,4,yscale="log")

            plot1.plot(t_print_array*1.0e-6,AP_print_array, color='r',label="$\mathrm{SecularMultiple}$")
            points = np.linspace(0.0,tend*1.0e-6,N)
            AP = 0.01 +2.0*np.pi*points/(t_1PN*1.0e-6)
            AP = (AP+np.pi)%(2.0*np.pi) - np.pi ### -pi < AP < pi
            plot1.plot(points,AP,color='g',label="$\mathrm{Analytic}$")

            plot2.plot(t_print_array*1.0e-6,np.fabs( (AP - AP_print_array)/AP ), color='r')
            plot3.plot(t_print_array*1.0e-6,np.fabs((a-a_print_array)/a), color='r')
            plot4.plot(t_print_array*1.0e-6,np.fabs((e-e_print_array)/e), color='r')

            fontsize = 15
            plot1.set_ylabel("$\omega$",fontsize=fontsize)
            plot2.set_ylabel("$|(\omega_p-\omega)/\omega_p|$",fontsize=fontsize)
            plot3.set_ylabel("$|(a_0-a)/a_0|$",fontsize=fontsize)
            plot4.set_ylabel("$|(e_0-e)/e_0|$",fontsize=fontsize)
            
            handles,labels = plot1.get_legend_handles_labels()
            plot1.legend(handles,labels,loc="upper left",fontsize=0.6*fontsize)

            pyplot.show()

    def test3(self,args):
        print("Test GW emission in 2-body system + collision detection")

        code = SecularMultiple()
        CONST_G = code.CONST_G
        CONST_C = code.CONST_C

        a0 = 1.0
        e0 = 0.999
        m1 = 1.0
        m2 = 1.0
        particles = Tools.create_nested_multiple(2,[m1, m2], [a0], [e0], [0.01], [0.01], [0.01])
        bodies = [x for x in particles if x.is_binary == False]
        binaries = [x for x in particles if x.is_binary == True]
        
        for b in binaries:
            b.include_pairwise_1PN_terms = False
            b.include_pairwise_25PN_terms = True
            b.check_for_physical_collision_or_orbit_crossing = True
        
        rg = (m1+m2)*CONST_G/(CONST_C**2)
        
        for b in bodies:
            b.radius = 100.0*rg

        binary = binaries[0]

        code.add_particles(particles)

        t_print_array = []
        a_print_array = []
        e_print_array = []
        AP_print_array = []

        tend = 1e8
        N = 1000
        dt = tend/float(N)
        t = 0.0
        while (t<tend):
            t+=dt

            code.evolve_model(t)
            flag = code.flag

            t_print_array.append(t*1.0e-6)
            a_print_array.append(binary.a)
            e_print_array.append(binary.e)
            AP_print_array.append(binary.AP)

            if args.verbose==True:
                print("t",t*1e-6,'a/AU',binary.a,'e',binary.e)
            
            if flag == 2:
                if args.verbose==True:
                    print( 'root found')
                break

        assert round(t*1e-6,1) == 97.3
        print("Test passed")
        
        code.reset()
        
        if HAS_MATPLOTLIB == True and args.plot==True:
            e_print_array = np.array(e_print_array)
            
            fig = pyplot.figure(figsize=(16,10))
            plot1 = fig.add_subplot(2,1,1)
            plot2 = fig.add_subplot(2,1,2,yscale="log")

            plot1.plot(t_print_array,e_print_array, color='r')

            plot2.plot(t_print_array,a_print_array, color='r')

            ### Peters 1964 ###
            c0 = a0*(1.0-e0**2)/( pow(e0,12.0/19.0)*pow(1.0 + (121.0/304.0)*e0**2,870.0/2299.0))
            a_an = c0*pow(e_print_array,12.0/19.0)*pow(1.0+(121.0/304.0)*e_print_array**2,870.0/2299.0)/(1.0-e_print_array**2)
            beta = (64.0/5.0)*CONST_G**3*m1*m2*(m1+m2)/(CONST_C**5)
            #T = c0**4*pow(e0,48.0/19.0)/(4.0*beta)
            T_c = a0**4/(4.0*beta)
            T = (768.0/425.0)*T_c*pow(1.0-e0**2,7.0/2.0)
            print( 'T/Myr (approx)',T*1.0e-6)
            plot2.plot(t_print_array,a_an,color='g',linestyle='dashed',linewidth=2)

            fontsize = 15
            plot1.set_ylabel("$e$",fontsize=fontsize)
            plot2.set_ylabel("$a/\mathrm{AU}$",fontsize=fontsize)
            plot2.set_xlabel("$t/\mathrm{Myr}$",fontsize=fontsize)

            pyplot.show()

    
    def test4(self,args):
        print("Test tidal friction in 2-body system")
        
        code = SecularMultiple()
        code.enable_tides = True

        CONST_G = code.CONST_G
        CONST_C = code.CONST_C
        CONST_R_SUN = code.CONST_R_SUN
        day = 1.0/365.25
        second = day/(24.0*3600.0)

        M = 0.0009546386983890755 ### Jupiter mass
        R = 40.0*0.1027922358015816*CONST_R_SUN ### 40 R_J
        m_per = 1.0
        mu = m_per*M/(m_per+M)
        a0 = 0.1
        e0 = 0.3
        P0 = 2.0*np.pi*np.sqrt(a0**3/(CONST_G*(M+m_per)))
        n0 = 2.0*np.pi/P0

        aF = a0*(1.0-e0**2)
        nF = np.sqrt( CONST_G*(M+m_per)/(aF**3) )

        particles = Tools.create_nested_multiple(2, [m_per, M], [a0], [e0], [0.01], [0.01], [0.01])
        binary = particles[2]
        
        particles[0].radius = CONST_R_SUN
        particles[1].radius = R
        particles[1].spin_vec_x = 0.0
        particles[1].spin_vec_y = 0.0
        particles[1].spin_vec_z = 4.0e-2/day

        k_L = 0.38
        k_AM = k_L/2.0
        rg = 0.25
        tau = 0.66*second

        I = rg*M*R**2
        alpha = I/(mu*a0**2)
        
        T = R**3/(CONST_G*M*tau)
        t_V = 3.0*(1.0 + 2.0*k_AM)**2*T/k_AM
        
        particles[0].include_tidal_friction_terms = False
        
        particles[1].tides_method = 1
        particles[1].include_tidal_friction_terms = True
        particles[1].include_tidal_bulges_precession_terms = False
        particles[1].include_rotation_precession_terms = False
        particles[1].minimum_eccentricity_for_tidal_precession = 1.0e-8

        particles[1].tides_apsidal_motion_constant = k_AM
        particles[1].tides_viscous_time_scale = t_V
        particles[1].tides_gyration_radius = rg

        particles[2].check_for_physical_collision_or_orbit_crossing = True

        code.add_particles(particles)
        binary = code.particles[2]

        t = 0.0
        N=100
        tend = 1.0e4
        dt = tend/float(N)

        t_print_array = []
        a_print_array = []
        n_print_array = []
        e_print_array = []
        AP_print_array = []
        spin_print_array = []

        while (t<tend):
            t+=dt
            code.evolve_model(t)
            if args.verbose==True:
                print( 'flag',code.flag,'t/yr',t,'a/AU',binary.a,'e',binary.e)


            t_print_array.append(t)
            a_print_array.append(binary.a)
            n_print_array.append(np.sqrt(CONST_G*(M+m_per)/(binary.a**3)))
            e_print_array.append(binary.e)
            AP_print_array.append(binary.AP)
            spin_print_array.append( np.sqrt( particles[1].spin_vec_x**2 + particles[1].spin_vec_y**2 + particles[1].spin_vec_z**2) )

            bodies = particles[0:2]
            if args.verbose==True:
                for body in bodies:
                    print( 'S_x',body.spin_vec_x)
                    print( 'S_y',body.spin_vec_y)
                    print( 'S_z',body.spin_vec_z)
                print( '='*50)

        N_r = 2
        assert round(spin_print_array[-1],N_r) == round(n_print_array[-1],N_r)
        assert round(a_print_array[-1],N_r) == round(aF,N_r)
        assert len([x for x in range(len(t_print_array)) if round(aF,N_r) not in [round(a*(1.0-e**2),N_r) for a,e in zip( a_print_array,e_print_array)] ] ) == 0
        print("Test passed")

        code.reset()
        
        if HAS_MATPLOTLIB == True and args.plot==True:
            fig = pyplot.figure(figsize=(10,10))
            fontsize=12
    
            t_print_array = np.array(t_print_array)
            a_print_array = np.array(a_print_array)
            e_print_array = np.array(e_print_array)
            AP_print_array = np.array(AP_print_array)
            spin_print_array = np.array(spin_print_array)
            n_print_array = np.array(n_print_array)
            
            N_p = 4
            plot1 = fig.add_subplot(N_p,1,1)
            plot1.plot(t_print_array*1.0e-6,a_print_array, color='r')
            plot1.set_ylabel("$a/\mathrm{AU}$",fontsize=fontsize)

            plot2 = fig.add_subplot(N_p,1,2)
            plot2.plot(t_print_array*1.0e-6,e_print_array,color='k')
            plot2.set_ylabel("$e$",fontsize=fontsize)

            plot3 = fig.add_subplot(N_p,1,3,yscale="log")

            plot3.plot(t_print_array*1.0e-6,a_print_array*(1.0-e_print_array**2),color='k')
            plot3.axhline(y = a0*(1.0 - e0**2), color='k')
            plot3.set_ylabel("$a(1-e^2)/\mathrm{AU}$",fontsize=fontsize)

            plot4 = fig.add_subplot(N_p,1,4)
            plot4.plot(t_print_array*1.0e-6,spin_print_array/n_print_array)
            plot4.set_ylabel("$\Omega/n$",fontsize=fontsize)

            plot4.set_xlabel("$t/\mathrm{Myr}$",fontsize=fontsize)

            pyplot.show()

    def test5(self,args):
        print("Test precession due to tidal bulges")

        code = SecularMultiple()
        code.enable_tides = True
        CONST_G = code.CONST_G
        CONST_C = code.CONST_C
        CONST_R_SUN = code.CONST_R_SUN
        day = 1.0/365.25
        second = day/(24.0*3600.0)

        M = 0.0009546386983890755 ### Jupiter mass
        R = 1.0*0.1027922358015816*CONST_R_SUN ### Jupiter radius ~ 0.1 R_SUN

        m_per = 1.0
        a0 = 30.0
        e0 = 0.999
        P0 = 2.0*np.pi*np.sqrt(a0**3/(CONST_G*(M+m_per)))
        n0 = 2.0*np.pi/P0

        particles = Tools.create_nested_multiple(2, [m_per, M], [a0], [e0], [0.01], [0.01], [0.01])
        binary = particles[2]
        particles[0].radius = 1.0*CONST_R_SUN
        particles[1].radius = R

        k_L = 0.41
        k_AM = k_L/2.0

        particles[1].tides_method = 0
        particles[1].include_tidal_friction_terms = False
        particles[1].include_tidal_bulges_precession_terms = True
        particles[1].include_rotation_precession_terms = False
        particles[1].minimum_eccentricity_for_tidal_precession = 1.0e-5
        particles[1].tides_apsidal_motion_constant = k_AM
        particles[1].tides_gyration_radius = 0.25
        
        code.add_particles(particles)

        t = 0.0
        dt = 1.0e6
        tend = 1.0e8

        t_print_array = []
        a_print_array = []
        e_print_array = []
        AP_print_array = []

        g_dot_TB = (15.0/8.0)*n0*(8.0+12.0*e0**2+e0**4)*(m_per/M)*k_AM*pow(R/a0,5.0)/pow(1.0-e0**2,5.0)
        t_TB = 2.0*np.pi/g_dot_TB

        while (t<tend):
            t+=dt
            code.evolve_model(t)
            if args.verbose==True:
                print( 'flag',code.flag,'t',t,'a/AU',binary.a,'e',binary.e)

            t_print_array.append(t*1.0e-6)
            a_print_array.append(binary.a)
            e_print_array.append(binary.e)
            AP_print_array.append(binary.AP)

        AP = 0.01 +2.0*np.pi*tend/(t_TB)
        AP = (AP+np.pi)%(2.0*np.pi) - np.pi ### -pi < AP < pi
        
        N_r = 8
        assert round(AP,N_r) == round(AP_print_array[-1],N_r)
        print("Test passed")

        code.reset()
        
        if HAS_MATPLOTLIB == True and args.plot==True:
            
            t_print_array = np.array(t_print_array)
            a_print_array = np.array(a_print_array)
            e_print_array = np.array(e_print_array)
            AP_print_array = np.array(AP_print_array)
            
            fig = pyplot.figure(figsize=(10,10))
            plot1 = fig.add_subplot(4,1,1)
            plot2 = fig.add_subplot(4,1,2,yscale="log")
            plot3 = fig.add_subplot(4,1,3,yscale="log")
            plot4 = fig.add_subplot(4,1,4,yscale="log")

            plot1.plot(t_print_array,AP_print_array, color='r')
            points = np.linspace(0.0,tend*1.0e-6,len(t_print_array))
            AP = 0.01 +2.0*np.pi*points/(t_TB*1.0e-6)
            AP = (AP+np.pi)%(2.0*np.pi) - np.pi ### -pi < AP < pi
            plot1.plot(points,AP,color='g',linestyle='dotted',linewidth=2)

            plot2.plot(t_print_array,np.fabs( (AP - AP_print_array)/AP ), color='r')
            plot3.plot(t_print_array,np.fabs((a0-a_print_array)/a0), color='r')
            plot4.plot(t_print_array,np.fabs((e0-e_print_array)/e0), color='r')

            fontsize = 15
            plot1.set_ylabel("$\omega/\mathrm{rad}$",fontsize=fontsize)
            plot2.set_ylabel("$|(\omega_p-\omega)/\omega_p|$",fontsize=fontsize)
            plot3.set_ylabel("$|(a_0-a)/a_0|$",fontsize=fontsize)
            plot4.set_ylabel("$|(e_0-e)/e_0|$",fontsize=fontsize)
            
            plot4.set_xlabel("$t/\mathrm{Myr}$",fontsize=fontsize)

            pyplot.show()

    def test6(self,args):
        print("Test precession due to rotation")

        code = SecularMultiple()
        code.enable_tides = True
        CONST_G = code.CONST_G
        CONST_C = code.CONST_C
        CONST_R_SUN = code.CONST_R_SUN
        day = 1.0/365.25
        second = day/(24.0*3600.0)
        
        M = 0.0009546386983890755 ### Jupiter mass
        R = 1.5*0.1027922358015816*CONST_R_SUN ### Jupiter radius ~ 0.1 R_SUN
        m_per = 1.0
        a0 = 30.0
        e0 = 0.999
        P0 = 2.0*np.pi*np.sqrt(a0**3/(CONST_G*(M+m_per)))
        n0 = 2.0*np.pi/P0

        aF = a0*(1.0-e0**2)
        nF = np.sqrt( CONST_G*(M+m_per)/(aF**3) )

        particles = Tools.create_nested_multiple(2, [m_per, M], [a0], [e0], [1.0e-5], [1.0e-5], [1.0e-5])
        binary = particles[2]
        particles[0].radius = 1.0
        particles[1].radius = R
        particles[1].spin_vec_x = 0.0
        particles[1].spin_vec_y = 0.0
        Omega_PS0 = n0*(33.0/10.0)*pow(a0/aF,3.0/2.0)
        particles[1].spin_vec_z = Omega_PS0

        k_L = 0.51
        k_AM = k_L/2.0
        rg = 0.25
        particles[1].tides_method = 1
        particles[1].include_tidal_friction_terms = False
        particles[1].include_tidal_bulges_precession_terms = False
        particles[1].include_rotation_precession_terms = True
        particles[1].minimum_eccentricity_for_tidal_precession = 1.0e-5
        particles[1].tides_apsidal_motion_constant = k_AM
        particles[1].tides_gyration_radius = rg

        code.add_particles(particles)

        t = 0.0
        dt = 1.0e6
        tend = 1.0e8

        t_print_array = []
        a_print_array = []
        e_print_array = []
        AP_print_array = []

        Omega_vec = [particles[1].spin_vec_x,particles[1].spin_vec_y,particles[1].spin_vec_z]
        Omega = np.sqrt(Omega_vec[0]**2 + Omega_vec[1]**2 + Omega_vec[2]**2)
        if args.verbose==True:
            print( 'Omega/n',Omega/n0)

        while (t<tend):
            t+=dt
            code.evolve_model(t)
            if args.verbose==True:
                print( 'flag',code.flag,'t',t,'a',binary.a,'e',binary.e)


            t_print_array.append(t*1.0e-6)
            a_print_array.append(binary.a)
            e_print_array.append(binary.e)
            AP_print_array.append(binary.AP)

        g_dot_rot = n0*(1.0 + m_per/M)*k_AM*pow(R/a0,5.0)*(Omega/n0)**2/((1.0-e0**2)**2)
        t_rot = 2.0*np.pi/g_dot_rot

        AP = 0.01 + 2.0*np.pi*tend/(t_rot)
        AP = (AP+np.pi)%(2.0*np.pi) - np.pi ### -pi < AP < pi

        N_r = 1
        assert round(AP,N_r) == round(AP_print_array[-1],N_r)
        print("Test passed")

        code.reset()
        
        if HAS_MATPLOTLIB == True and args.plot==True:
            t_print_array = np.array(t_print_array)
            a_print_array = np.array(a_print_array)
            e_print_array = np.array(e_print_array)
            AP_print_array = np.array(AP_print_array)

            fig = pyplot.figure(figsize=(10,10))
            plot1 = fig.add_subplot(4,1,1)
            plot2 = fig.add_subplot(4,1,2,yscale="log")
            plot3 = fig.add_subplot(4,1,3,yscale="log")
            plot4 = fig.add_subplot(4,1,4,yscale="log")

            plot1.plot(t_print_array,AP_print_array, color='r')
            points = np.linspace(0.0,tend*1.0e-6,len(t_print_array))
            AP = 0.01 +2.0*np.pi*points/(t_rot*1.0e-6)
            AP = (AP+np.pi)%(2.0*np.pi) - np.pi ### -pi < AP < pi
            plot1.plot(points,AP,color='g',linestyle='dotted',linewidth=2)

            plot2.plot(t_print_array,np.fabs( (AP - AP_print_array)/AP ), color='r')
            plot3.plot(t_print_array,np.fabs((a0-a_print_array)/a0), color='r')
            plot4.plot(t_print_array,np.fabs((e0-e_print_array)/e0), color='r')

            fontsize = 15
            plot1.set_ylabel("$\omega/\mathrm{rad}$",fontsize=fontsize)
            plot2.set_ylabel("$|(\omega_p-\omega)/\omega_p|$",fontsize=fontsize)
            plot3.set_ylabel("$|(a_0-a)/a_0|$",fontsize=fontsize)
            plot4.set_ylabel("$|(e_0-e)/e_0|$",fontsize=fontsize)

            plot4.set_xlabel("$t/\mathrm{Myr}$",fontsize=fontsize)
            pyplot.show()

    def test7(self,args):
        print("Test collision detection in 3-body system")

        code = SecularMultiple()
        
        particles = Tools.create_nested_multiple(3,[1.0, 1.2, 0.9], [1.0, 100.0], [0.1, 0.5], [0.01, 80.0*np.pi/180.0], [0.01, 0.01], [0.01, 0.01])
        bodies = [x for x in particles if x.is_binary==False]
        binaries = [x for x in particles if x.is_binary==True]

        binaries[0].check_for_physical_collision_or_orbit_crossing = True
        R = 0.03 ### AU
        for body in bodies:
            body.radius = R

        code.add_particles(particles)

        t = 0.0
        dt = 1.0e4
        tend = 1.0e6
        t_root = 0.0
        
        t_print_array = []
        a_print_array = []
        e_print_array = []

        while (t<tend):
            t+=dt
            code.evolve_model(t)
            flag = code.flag

            if args.verbose==True:
                print("="*50)
                print("t/Myr",t*1e-6,"rp/AU",binaries[0].a*(1.0 - binaries[0].e) )
                print( 'secular_breakdown_has_occurred',binaries[0].secular_breakdown_has_occurred)
                print( 'dynamical_instability_has_occurred',binaries[0].dynamical_instability_has_occurred)
                print( 'physical_collision_or_orbit_crossing_has_occurred',binaries[0].physical_collision_or_orbit_crossing_has_occurred)
                print( 'minimum_periapse_distance_has_occurred',binaries[0].minimum_periapse_distance_has_occurred)
                print( 'RLOF_at_pericentre_has_occurred',binaries[0].RLOF_at_pericentre_has_occurred)

            t_print_array.append(t*1.0e-6)
            a_print_array.append(binaries[0].a)
            e_print_array.append(binaries[0].e)

            if flag == 2:
                t_root = code.model_time
                if args.verbose==True:
                    print( 'root found at t=',t_root)
                break
        
        assert all([x.secular_breakdown_has_occurred for x in particles]) == False
        assert all([x.dynamical_instability_has_occurred for x in particles]) == False
        assert all([x.RLOF_at_pericentre_has_occurred for x in particles]) == False
        assert all([x.minimum_periapse_distance_has_occurred for x in particles]) == False
        assert binaries[0].physical_collision_or_orbit_crossing_has_occurred == True

        N_r = 5
        assert round(a_print_array[-1]*(1.0 - e_print_array[-1]),N_r) == round(2.0*R,N_r)
        print("Test passed")

        code.reset()
        
        if HAS_MATPLOTLIB == True and args.plot==True:
            a_print_array = np.array(a_print_array)
            e_print_array = np.array(e_print_array)
            
            fig = pyplot.figure()
            plot = fig.add_subplot(1,1,1)
            plot.plot(t_print_array,a_print_array*(1.0-e_print_array))
            plot.axhline(y = bodies[0].radius + bodies[1].radius,color='k')
            plot.set_ylabel("$r_\mathrm{p}/\mathrm{AU}$")
            plot.set_xlabel("$t/\mathrm{Myr}$")

            pyplot.show()

    def test8(self,args):
        print("Test RLOF in 3-body system")

        code = SecularMultiple()
        
        particles = Tools.create_nested_multiple(3,[1.0, 1.2, 0.9], [1.0, 100.0], [0.1, 0.5], [0.01, 80.0*np.pi/180.0], [0.01, 0.01], [0.01, 0.01])
        bodies = [x for x in particles if x.is_binary==False]
        binaries = [x for x in particles if x.is_binary==True]

        binaries[0].check_for_physical_collision_or_orbit_crossing = True
        bodies[0].check_for_RLOF_at_pericentre = True
        R = 0.03 ### AU
        for body in bodies:
            body.radius = R

        code.add_particles(particles)

        t = 0.0
        dt = 1.0e4
        tend = 1.0e6
        t_root = 0.0
        
        t_print_array = []
        a_print_array = []
        e_print_array = []

        while (t<tend):
            t+=dt
            code.evolve_model(t)
            flag = code.flag

            if args.verbose==True:
                print("="*50)
                print("t/Myr",t*1e-6,"rp/AU",binaries[0].a*(1.0 - binaries[0].e) )
                print( 'secular_breakdown_has_occurred',binaries[0].secular_breakdown_has_occurred)
                print( 'dynamical_instability_has_occurred',binaries[0].dynamical_instability_has_occurred)
                print( 'physical_collision_or_orbit_crossing_has_occurred',binaries[0].physical_collision_or_orbit_crossing_has_occurred)
                print( 'minimum_periapse_distance_has_occurred',binaries[0].minimum_periapse_distance_has_occurred)
                print( 'RLOF_at_pericentre_has_occurred',bodies[0].RLOF_at_pericentre_has_occurred)

            t_print_array.append(t*1.0e-6)
            a_print_array.append(binaries[0].a)
            e_print_array.append(binaries[0].e)

            if flag == 2:
                t_root = code.model_time
                if args.verbose==True:
                    print( 'root found at t=',t_root)
                break

        assert all([x.secular_breakdown_has_occurred for x in particles]) == False
        assert all([x.dynamical_instability_has_occurred for x in particles]) == False
        assert all([x.physical_collision_or_orbit_crossing_has_occurred for x in particles]) == False
        assert all([x.minimum_periapse_distance_has_occurred for x in particles]) == False
        assert bodies[0].RLOF_at_pericentre_has_occurred == True

        q = bodies[0].mass/bodies[1].mass
        f_q = 0.49*pow(q,2.0/3.0)/( 0.6*pow(q,2.0/3.0) + np.log(1.0 + pow(q,1.0/3.0)) )
        r_RLOF = bodies[0].radius/f_q
        
        N_r = 10
        assert round(a_print_array[-1]*(1.0 - e_print_array[-1]),N_r) == round(r_RLOF,N_r)
        print("Test passed")

        code.reset()
        
        if HAS_MATPLOTLIB == True and args.plot==True:
            a_print_array = np.array(a_print_array)
            e_print_array = np.array(e_print_array)
            
            fig = pyplot.figure()
            plot = fig.add_subplot(1,1,1)
            plot.plot(t_print_array,a_print_array*(1.0-e_print_array))
            plot.axhline(y = bodies[0].radius + bodies[1].radius,color='k')
            plot.set_ylabel("$r_\mathrm{p}/\mathrm{AU}$")
            plot.set_xlabel("$t/\mathrm{Myr}$")

            pyplot.show()
            
    def test9(self,args):
        print("Test minimum periapse occurrence")

        code = SecularMultiple()
        
        particles = Tools.create_nested_multiple(3,[1.0, 1.2, 0.9], [1.0, 100.0], [0.1, 0.5], [0.01, 80.0*np.pi/180.0], [0.01, 0.01], [0.01, 0.01])
        bodies = [x for x in particles if x.is_binary==False]
        binaries = [x for x in particles if x.is_binary==True]

        binaries[0].check_for_minimum_periapse_distance = True
        rp_min = 0.1
        binaries[0].check_for_minimum_periapse_distance_value = rp_min
        
        code.add_particles(particles)

        t = 0.0
        dt = 1.0e4
        tend = 1.0e6
        t_root = 0.0
        
        t_print_array = []
        a_print_array = []
        e_print_array = []

        while (t<tend):
            t+=dt
            code.evolve_model(t)
            flag = code.flag

            if args.verbose==True:
                print("="*50)
                print("t/Myr",t*1e-6,"rp/AU",binaries[0].a*(1.0 - binaries[0].e) )
                print( 'secular_breakdown_has_occurred',binaries[0].secular_breakdown_has_occurred)
                print( 'dynamical_instability_has_occurred',binaries[0].dynamical_instability_has_occurred)
                print( 'physical_collision_or_orbit_crossing_has_occurred',binaries[0].physical_collision_or_orbit_crossing_has_occurred)
                print( 'minimum_periapse_distance_has_occurred',binaries[0].minimum_periapse_distance_has_occurred)
                print( 'RLOF_at_pericentre_has_occurred',bodies[0].RLOF_at_pericentre_has_occurred)

            t_print_array.append(t*1.0e-6)
            a_print_array.append(binaries[0].a)
            e_print_array.append(binaries[0].e)

            if flag == 2:
                t_root = code.model_time
                if args.verbose==True:
                    print( 'root found at t=',t_root)
                break
        
        assert all([x.secular_breakdown_has_occurred for x in particles]) == False
        assert all([x.dynamical_instability_has_occurred for x in particles]) == False
        assert all([x.physical_collision_or_orbit_crossing_has_occurred for x in particles]) == False
        assert all([x.RLOF_at_pericentre_has_occurred for x in particles]) == False
        assert binaries[0].minimum_periapse_distance_has_occurred == True

        N_r = 5
        assert round(a_print_array[-1]*(1.0 - e_print_array[-1]),N_r) == round(rp_min,N_r)
        print("Test passed")

        code.reset()
        
        if HAS_MATPLOTLIB == True and args.plot==True:
            a_print_array = np.array(a_print_array)
            e_print_array = np.array(e_print_array)
            
            fig = pyplot.figure()
            plot = fig.add_subplot(1,1,1)
            plot.plot(t_print_array,a_print_array*(1.0-e_print_array))
            plot.axhline(y = rp_min,color='k')
            plot.set_ylabel("$r_\mathrm{p}/\mathrm{AU}$")
            plot.set_xlabel("$t/\mathrm{Myr}$")

            pyplot.show()

    def test10(self,args):
        print("Test adiabatic mass loss")

        code = SecularMultiple()
        
        m1i = 1.0
        m2i = 1.2
        m3i = 0.9
        a1i = 1.0
        a2i = 100.0
        particles = Tools.create_nested_multiple(3,[m1i,m2i,m3i], [a1i,a2i], [0.1, 0.5], [0.01, 80.0*np.pi/180.0], [0.01, 0.01], [0.01, 0.01])
        bodies = [x for x in particles if x.is_binary==False]
        binaries = [x for x in particles if x.is_binary==True]

        m1dot = -1.0e-7
        m2dot = -1.0e-8
        m3dot = -1.0e-9
        mdots = [m1dot,m2dot,m3dot]
        for index,body in enumerate(bodies):
            body.mass_dot = mdots[index]

        code.add_particles(particles)

        t = 0.0
        dt = 1.0e4
        tend = 1.0e6

        t_print_array = []
        a1_print_array = []
        a2_print_array = []
        e_print_array = []

        while (t<tend):
            t+=dt
            code.evolve_model(t)
            flag = code.flag

            if args.verbose==True:
                print( 't/Myr',t*1e-6,'m1',bodies[0].mass,'m2',bodies[1].mass,'m3',bodies[2].mass,'a/AU',binaries[0].a)

            t_print_array.append(t*1.0e-6)
            a1_print_array.append(binaries[0].a)
            a2_print_array.append(binaries[1].a)
            e_print_array.append(binaries[0].e)

        m1 = m1i + m1dot*tend
        m2 = m2i + m2dot*tend
        m3 = m3i + m3dot*tend
            
        a1 = a1i*(m1i+m2i)/(m1+m2)
        a2 = a2i*(m1i+m2i+m3i)/(m1+m2+m3)

        N_r = 4
        assert round(a1,N_r) == round(a1_print_array[-1],N_r)
        assert round(a2,N_r) == round(a2_print_array[-1],N_r)
        print("Test passed")

        code.reset()
        
        if HAS_MATPLOTLIB == True and args.plot==True:
            a1_print_array = np.array(a1_print_array)
            a2_print_array = np.array(a2_print_array)
            e_print_array = np.array(e_print_array)

            t = pow(10.0,np.linspace(4.0,6.0,100))
            m1 = m1i + m1dot*t
            m2 = m2i + m2dot*t
            m3 = m3i + m3dot*t
            
            a1 = a1i*(m1i+m2i)/(m1+m2)
            a2 = a2i*(m1i+m2i+m3i)/(m1+m2+m3)

            fig = pyplot.figure(figsize=(10,8))
            plot1 = fig.add_subplot(2,1,1,yscale="log")
            plot2 = fig.add_subplot(2,1,2,yscale="log")
            plot1.plot(t_print_array,a1_print_array,color='k',linestyle='solid',label='$a_1$',zorder=10)
            plot2.plot(t_print_array,a2_print_array,color='k',linestyle='solid',label='$a_2$',zorder=10)
            
            plot1.plot(t*1.0e-6,a1,color='g',linestyle='dashed',linewidth=3,label='$a_1\,(\mathrm{an})$')
            plot2.plot(t*1.0e-6,a2,color='g',linestyle='dashed',linewidth=3,label='$a_2\,(\mathrm{an})$')

            handles,labels = plot1.get_legend_handles_labels()
            plot1.legend(handles,labels,loc="lower left",fontsize=18)

            plot1.set_ylabel("$a_1$")
            plot2.set_ylabel("$a_2$")
            plot2.set_xlabel("$t/\mathrm{Myr}$")

            pyplot.show()


    def test11(self,args):
        print("Test hybrid integration")

        m1=1.0
        m2=1.0e-6
        m3=1.0
        e1=0
        e2=0.4
        a1=1.0
        a2=10.0

        i1=0.01
        i2=65.0*np.pi/180.0
        AP1=0
        AP2=0
        LAN1=0
        LAN2=0

        particles = Tools.create_nested_multiple(3, [m1,m2,m3],[a1,a2],[e1,e2],[i1,i2],[AP1,AP2],[LAN1,LAN2])
        
        bodies = [x for x in particles if x.is_binary==False]
        binaries = [x for x in particles if x.is_binary==True]
        N_binaries = len(binaries)
        
        code = SecularMultiple()
        code.add_particles(particles)

        integration_methods = [0,1]
        KS_use_V = [True,True]
        terms = [False,True,True,True,True,True]
        
        binaries[0].integration_method = integration_methods[0]
        binaries[1].integration_method = integration_methods[1]

        binaries[0].KS_use_perturbing_potential = KS_use_V[0]
        binaries[1].KS_use_perturbing_potential = KS_use_V[1]

        CONST_G = code.CONST_G
        P1=2.0*np.pi*np.sqrt(a1**3/(CONST_G*(m1+m2)))
        P2=2.0*np.pi*np.sqrt(a2**3/(CONST_G*(m1+m2+m3)))
        P_LK12 = (P2**2/P1)*((m1+m2+m3)/m3)*pow(1.0-e2**2,3.0/2.0)
        if args.verbose==True:
            print("P_orbs/yr",P1,P2)
            print("P_LK/yr",P_LK12)

        code.include_double_averaging_corrections = terms[0]
        code.include_quadrupole_order_terms = terms[1]
        code.include_octupole_order_binary_pair_terms = terms[2]
        code.include_octupole_order_binary_triplet_terms = terms[3]
        code.include_hexadecupole_order_binary_pair_terms = terms[4]
        code.include_dotriacontupole_order_binary_pair_terms = terms[5]
        
        a_print = [[] for x in range(N_binaries)]
        e_print = [[] for x in range(N_binaries)]
        t_print = []
        rel_INCL_print = []
        

        code.enable_root_finding = True
        binaries[0].check_for_physical_collision_or_orbit_crossing=True
        bodies[0].radius=1.0e-5
        bodies[1].radius=1.0e-5
        
        import time
        
        t = 0.0
        N = 1000
        tend = 1.e3
        dt = tend/float(N)
                
        start = time.time()
        while t<tend:
            t+=dt
            code.evolve_model(t)
            
            if args.verbose==True:
                print( 't/Myr',t*1e-6,'es',[x.e for x in binaries],'smas',[x.a for x in binaries])

            rel_INCL_print.append(binaries[0].INCL_parent)                        
            for i in range(N_binaries):
                a_print[i].append(binaries[i].a)
                e_print[i].append(binaries[i].e)
            t_print.append(t)
            
            flag=code.flag
            if flag==2:
                print("RF")
                break
        wall_time = time.time()-start

        t_print = np.array(t_print)
        rel_INCL_print = np.array(rel_INCL_print)
        for i in range(N_binaries):
            a_print[i] = np.array(a_print[i])
            e_print[i] = np.array(e_print[i])

        N_r = 4
        #assert round(e_print[0][-1],N_r) == 0.5274
        print("Test passed")

        code.reset()
        
        if HAS_MATPLOTLIB==True and args.plot==True:
            if 1==0:
                pyplot.rc('text',usetex=True)
                pyplot.rc('legend',fancybox=True)

            
            fig=pyplot.figure(figsize=(10,8))
            plot1=fig.add_subplot(2,1,1)
            plot2=fig.add_subplot(2,1,2,yscale="log")

            plot1.plot(1.0e-6*t_print,rel_INCL_print*180.0/np.pi)
            plot2.plot(1.0e-6*t_print,1-e_print[0])

            fontsize=18

            plot1.set_ylabel("$i_\mathrm{rel}\,(\mathrm{deg})$",fontsize=fontsize)
            plot2.set_ylabel("$1-e$",fontsize=fontsize)

            plot2.set_xlabel("$t/\mathrm{Myr}$")
            
            pyplot.show()

    def test12(self,args):
        print("Test flybys module: instantaneous change -- SNe in binary")

        code = SecularMultiple()
        CONST_G = code.CONST_G
        CONST_km_per_s_to_AU_per_yr = code.CONST_km_per_s_to_AU_per_yr
                
        a1 = 10.0
        e1 = 0.1
        m1 = 1.0
        m2 = 0.8

        INCL1 = 0.1
        AP1 = 0.2
        LAN1 = 0.3
        f1 = 60.5*np.pi/180.0

        particles = Tools.create_nested_multiple(2, [m1,m2], [a1], [e1], [INCL1], [AP1], [LAN1] )

        binary = particles[2]
        binary.sample_orbital_phase_randomly = False
        binary.TA = f1
        
        delta_m1 = -0.5
        V_k_vec = np.array([0.0,1.0,2.0])*CONST_km_per_s_to_AU_per_yr
        #V_k_vec = np.array([0.0,0.0,0.0])

        particles[0].instantaneous_perturbation_delta_mass = delta_m1
        particles[0].instantaneous_perturbation_delta_VX = V_k_vec[0]
        particles[0].instantaneous_perturbation_delta_VY = V_k_vec[1]
        particles[0].instantaneous_perturbation_delta_VZ = V_k_vec[2]

        code.add_particles(particles)

        if args.verbose==True:
            print( '='*50)
            print( 'pre')
            print( 'a',binary.a,'e',binary.e,'INCL',binary.INCL*180.0/np.pi,'AP',binary.AP*180.0/np.pi,'LAN',binary.LAN*180.0/np.pi,binary.mass,'TA',binary.TA)

        code.apply_user_specified_instantaneous_perturbation()
        
        if args.verbose==True:
            print( '='*50)
            print( 'post')
            print( 'a',binary.a,'e',binary.e,'INCL',binary.INCL*180.0/np.pi,'AP',binary.AP*180.0/np.pi,'LAN',binary.LAN*180.0/np.pi,binary.mass,'TA',binary.TA)

        ### Compute analytic result (e.g., https://ui.adsabs.harvard.edu/abs/2016ComAC...3....6T/abstract) ###
        r1 = a1*(1.0-e1**2)/(1.0 + e1*np.cos(f1))
        v1_tilde = np.sqrt( CONST_G*(m1+m2)/(a1*(1.0-e1**2) ) )
        e1_vec_hat,j1_vec_hat = compute_e_and_j_hat_vectors(INCL1,AP1,LAN1)
        q1_vec_hat = np.cross(j1_vec_hat,e1_vec_hat)
        r1_vec = r1*( e1_vec_hat * np.cos(f1) + q1_vec_hat * np.sin(f1) )
        v1_vec = v1_tilde*( -e1_vec_hat * np.sin(f1) + q1_vec_hat * (e1 + np.cos(f1) ) )

        r1_dot_v1 = np.sum([x*y for x,y in zip(r1_vec,v1_vec)])
        r1_dot_V_k = np.sum([x*y for x,y in zip(r1_vec,V_k_vec)])
        v1_dot_V_k = np.sum([x*y for x,y in zip(v1_vec,V_k_vec)])
        V_k_dot_V_k = np.sum([x*y for x,y in zip(V_k_vec,V_k_vec)])
        v1c_sq = CONST_G*(m1+m2)/a1
        
        a1_p = a1*(1.0 + delta_m1/(m1+m2))*pow( 1.0 + 2.0*(a1/r1)*(delta_m1/(m1+m2)) - 2.0*v1_dot_V_k/v1c_sq - V_k_dot_V_k/v1c_sq, -1.0)
        j1_p = pow( (m1+m2)/(m1+m2+delta_m1), 2.0)*(1.0 + 2.0*(a1/r1)*(delta_m1/(m1+m2)) - 2.0*v1_dot_V_k/v1c_sq - V_k_dot_V_k/v1c_sq)*( 1.0 - e1**2 \
            + (1.0/(CONST_G*(m1+m2)*a1))*( r1**2*( 2.0*v1_dot_V_k + V_k_dot_V_k) - 2.0*r1_dot_v1*r1_dot_V_k - r1_dot_V_k**2) )
        e1_p = np.sqrt(1.0 - j1_p)
        
        if args.verbose==True:
            print( 'analytic results Toonen+16: ','new a1 = ',a1_p,'; new e1 = ',e1_p)
        
        N_r = 10
        assert round(binary.a,N_r) == round(a1_p,N_r)
        assert round(binary.e,N_r) == round(e1_p,N_r)
        
        print("Test passed")

        code.reset()
        
    def test13(self,args):
        print("Test flybys module: instantaneous change -- SNe in triple")

        code = SecularMultiple()
        CONST_G = code.CONST_G
        CONST_km_per_s_to_AU_per_yr = code.CONST_km_per_s_to_AU_per_yr        
        
        m1 = 1.0
        m2 = 0.8
        m3 = 1.2
        a1 = 10.0
        a2 = 100.0
        e1 = 0.1
        e2 = 0.3
        INCL1 = 0.1
        INCL2 = 0.5
        AP1 = 0.1
        AP2 = 1.0
        LAN1 = 0.1
        LAN2 = 2.0
        f1 = 60.5*np.pi/180.0
        f2 = 30.5*np.pi/180.0

        INCLs = [INCL1,INCL2]
        APs = [AP1,AP2]
        LANs = [LAN1,LAN2]
        masses = [m1,m2,m3]
        particles = Tools.create_nested_multiple(3,masses, [a1,a2], [e1,e2], INCLs, APs, LANs)
        
        inner_binary = particles[3]
        outer_binary = particles[4]
        inner_binary.sample_orbital_phase_randomly = 0
        outer_binary.sample_orbital_phase_randomly = 0
        inner_binary.TA = f1
        outer_binary.TA = f2
        
        delta_m1 = -0.3
        
        km_p_s_to_AU_p_yr = 0.21094502112788768
        V_k_vec = np.array([1.0,2.0,2.0])*CONST_km_per_s_to_AU_per_yr
        V_k_vec = np.array([0.0,0.0,0.0])
        
        particles[0].instantaneous_perturbation_delta_mass = delta_m1
        particles[0].instantaneous_perturbation_delta_VX = V_k_vec[0]
        particles[0].instantaneous_perturbation_delta_VY = V_k_vec[1]
        particles[0].instantaneous_perturbation_delta_VZ = V_k_vec[2]

        code.add_particles(particles)
        
        if args.verbose==True:
            print( '='*50)
            print( 'pre')
            print( 'inner','a',inner_binary.a,'e',inner_binary.e,'INCL',inner_binary.INCL*180.0/np.pi,'AP',inner_binary.AP*180.0/np.pi,'LAN',inner_binary.LAN*180.0/np.pi,'m',inner_binary.mass)
            print( 'outer','a',outer_binary.a,'e',outer_binary.e,'INCL',outer_binary.INCL*180.0/np.pi,'AP',outer_binary.AP*180.0/np.pi,'LAN',outer_binary.LAN*180.0/np.pi,'m',outer_binary.mass)
        
        code.apply_user_specified_instantaneous_perturbation()
        
        if args.verbose==True:
            print( '='*50)
            print( 'post')
            print( 'inner','a',inner_binary.a,'e',inner_binary.e,'INCL',inner_binary.INCL*180.0/np.pi,'AP',inner_binary.AP*180.0/np.pi,'LAN',inner_binary.LAN*180.0/np.pi,'m',inner_binary.mass)
            print( 'outer','a',outer_binary.a,'e',outer_binary.e,'INCL',outer_binary.INCL*180.0/np.pi,'AP',outer_binary.AP*180.0/np.pi,'LAN',outer_binary.LAN*180.0/np.pi,'m',outer_binary.mass)

        
        ### Compute analytic result (e.g., https://ui.adsabs.harvard.edu/abs/2016ComAC...3....6T/abstract) ###
        r1 = a1*(1.0-e1**2)/(1.0 + e1*np.cos(f1))
        v1_tilde = np.sqrt( CONST_G*(m1+m2)/(a1*(1.0-e1**2) ) )
        e1_vec_hat,j1_vec_hat = compute_e_and_j_hat_vectors(INCL1,AP1,LAN1)
        q1_vec_hat = np.cross(j1_vec_hat,e1_vec_hat)
        r1_vec = r1*( e1_vec_hat * np.cos(f1) + q1_vec_hat * np.sin(f1) )
        v1_vec = v1_tilde*( -e1_vec_hat * np.sin(f1) + q1_vec_hat * (e1 + np.cos(f1) ) )

        r1_dot_v1 = np.sum([x*y for x,y in zip(r1_vec,v1_vec)])
        r1_dot_V_k = np.sum([x*y for x,y in zip(r1_vec,V_k_vec)])
        v1_dot_V_k = np.sum([x*y for x,y in zip(v1_vec,V_k_vec)])
        V_k_dot_V_k = np.sum([x*y for x,y in zip(V_k_vec,V_k_vec)])
        v1c_sq = CONST_G*(m1+m2)/a1

        r2 = a2*(1.0-e2**2)/(1.0 + e2*np.cos(f2))
        v2_tilde = np.sqrt( CONST_G*(m1+m2+m3)/(a2*(1.0-e2**2) ) )
        e2_vec_hat,j2_vec_hat = compute_e_and_j_hat_vectors(INCL2,AP2,LAN2)
        q2_vec_hat = np.cross(j2_vec_hat,e2_vec_hat)
        r2_vec = r2*( e2_vec_hat * np.cos(f2) + q2_vec_hat * np.sin(f2) )
        v2_vec = v2_tilde*( -e2_vec_hat * np.sin(f2) + q2_vec_hat * (e2 + np.cos(f2) ) )
    
        Delta_r2_vec = (delta_m1/( (m1+m2) + delta_m1) ) * (m2/(m1+m2)) * r1_vec
        Delta_v2_vec = (delta_m1/( (m1+m2) + delta_m1) ) * ( (m2/(m1+m2)) * v1_vec + V_k_vec*(1.0 + m1/delta_m1) )
        r2_vec_p = r2_vec + Delta_r2_vec
        r2p = np.sqrt(np.dot(r2_vec_p,r2_vec_p))


        r2_dot_v2 = np.sum([x*y for x,y in zip(r2_vec,v2_vec)])
        r2_dot_V_k = np.sum([x*y for x,y in zip(r2_vec,V_k_vec)])
        v2c_sq = CONST_G*(m1+m2+m3)/a2
        v2_dot_Delta_v2_vec = np.dot(v2_vec,Delta_v2_vec)
        Delta_v2_vec_dot_Delta_v2_vec = np.dot(Delta_v2_vec,Delta_v2_vec)
        
        a1_p = a1*(1.0 + delta_m1/(m1+m2))*pow( 1.0 + 2.0*(a1/r1)*(delta_m1/(m1+m2)) - 2.0*v1_dot_V_k/v1c_sq - V_k_dot_V_k/v1c_sq, -1.0)
        j1_p = pow( (m1+m2)/(m1+m2+delta_m1), 2.0)*(1.0 + 2.0*(a1/r1)*(delta_m1/(m1+m2)) - 2.0*v1_dot_V_k/v1c_sq - V_k_dot_V_k/v1c_sq)*( 1.0 - e1**2 \
            + (1.0/(CONST_G*(m1+m2)*a1))*( r1**2*( 2.0*v1_dot_V_k + V_k_dot_V_k) - 2.0*r1_dot_v1*r1_dot_V_k - r1_dot_V_k**2) )
        e1_p = np.sqrt(1.0 - j1_p)

        a2_p = a2*(1.0 + delta_m1/(m1+m2+m3))*pow( 1.0 + 2.0*(a2/r2p)*(delta_m1/(m1+m2+m3)) - 2.0*v2_dot_Delta_v2_vec/v2c_sq - Delta_v2_vec_dot_Delta_v2_vec/v2c_sq + 2.0*a2*(r2-r2p)/(r2*r2p), -1.0)

        alpha = (-delta_m1/(m1+m2+delta_m1)) * m2/(m1+m2)
        j2_p = ((m1+m2+m3)/(m1+m2+m3+delta_m1))**2 * (1.0 + 2.0*(a2/r2p)*(delta_m1/(m1+m2+m3)) + 2.0*a2*(r2-r2p)/(r2*r2p) - 2.0*np.dot(v2_vec,Delta_v2_vec)/v2c_sq - Delta_v2_vec_dot_Delta_v2_vec/v2c_sq)*( (1.0-e2**2) + (1.0/(CONST_G*(m1+m2+m3)*a2))*( r2**2*(2.0*np.dot(v2_vec,Delta_v2_vec) + np.dot(Delta_v2_vec,Delta_v2_vec)) + (-2.0*alpha*np.dot(r1_vec,r2_vec) + alpha**2*r1**2)*np.dot(v2_vec + Delta_v2_vec,v2_vec+Delta_v2_vec) + 2.0*np.dot(r2_vec,v2_vec)*( alpha*np.dot(r1_vec,v2_vec) - np.dot(r2_vec,Delta_v2_vec) + alpha*np.dot(r1_vec,Delta_v2_vec)) - (-alpha*np.dot(r1_vec,v2_vec) + np.dot(r2_vec,Delta_v2_vec) - alpha*np.dot(r1_vec,Delta_v2_vec))**2 ) ) 
        e2_p = np.sqrt(1.0 - j2_p)
        
        if args.verbose==True:
            print( 'analytic results Toonen+16: ','new a1 = ',a1_p,'; new e1 = ',e1_p)
            print( 'analytic results Toonen+16: ','new a2 = ',a2_p,'; new e2 = ',e2_p)
        
        N_r = 10
        assert round(inner_binary.a,N_r) == round(a1_p,N_r)
        assert round(inner_binary.e,N_r) == round(e1_p,N_r)

        assert round(outer_binary.a,N_r) == round(a2_p,N_r)
        assert round(outer_binary.e,N_r) == round(e2_p,N_r)

        print("Test passed")

        code.reset()
        
    def test14(self,args):
        print("Test flybys module: numerically integrating over perturber's orbit")

        code = SecularMultiple()
        CONST_G = code.CONST_G
        
        ### binary orbit ###
        a = 1.0
        e = 0.1
        m1 = 1.0
        m2 = 0.8
        M_per = 1.0
        E = 2.0
        Q = 100.0
        INCL = 0.4*np.pi
        AP = 0.25*np.pi
        LAN = 0.25*np.pi

        masses = [m1,m2]
        m = m1 + m2
        particles = Tools.create_nested_multiple(2,masses, [a], [e], [INCL], [AP], [LAN])

        t_per = np.sqrt(CONST_G*(m+M_per)/(Q**3))

        t = 0.0
        t_ref = 1.0e4
        tend = 4.0*t_ref
        Nsteps = 1000
        dt = tend/float(Nsteps)

        external_particle = Particle(mass = M_per, is_binary=True, is_external=True, external_t_ref=t_ref, e=E, external_r_p = Q, INCL = 1.0e-10, AP = 1.0e-10, LAN = 1.0e-10)

        particles.append(external_particle)

        code = SecularMultiple()
        code.add_particles(particles)
        binary = code.particles[2]
        
        code.include_quadrupole_order_terms = True
        code.include_octupole_order_binary_pair_terms = True
        code.include_hexadecupole_order_binary_pair_terms = False
        code.include_dotriacontupole_order_binary_pair_terms = False

        t_print_array = []
        a_print_array = []
        e_print_array = []
        INCL_print_array = []
        AP_print_array = []
        LAN_print_array = []
        
        while (t<tend):
            t+=dt
            code.evolve_model(t)
             
            t_print_array.append(t)
            a_print_array.append(binary.a)
            e_print_array.append(binary.e)
            
        Delta_e = binary.e - e
            
        ### compute analytic result (https://ui.adsabs.harvard.edu/abs/2019MNRAS.487.5630H/abstract) ###
        e_vec_hat,j_vec_hat = compute_e_and_j_hat_vectors(INCL,AP,LAN)
        e_vec = e_vec_hat*e
        j_vec = j_vec_hat*np.sqrt(1.0-e**2)

        ex = e_vec[0]
        ey = e_vec[1]
        ez = e_vec[2]
        jx = j_vec[0]
        jy = j_vec[1]
        jz = j_vec[2]

        eps_SA = (M_per/np.sqrt(m*(m+M_per)))*pow(a/Q,3.0/2.0)*pow(1.0 + E,-3.0/2.0)
        eps_oct = (a/Q)*(m1-m2)/((1.0+E)*m)
        Delta_e_an = (5*eps_SA*(np.sqrt(1 - E**(-2))*((1 + 2*E**2)*ey*ez*jx + (1 - 4*E**2)*ex*ez*jy + 2*(-1 + E**2)*ex*ey*jz) + 3*E*ez*(ey*jx - ex*jy)*np.arccos(-1.0/E)))/(2.*E*np.sqrt(ex**2 + ey**2 + ez**2))
        
        Delta_e_an += -(5*eps_oct*eps_SA*(np.sqrt(1 - E**(-2))*(ez*jy*(14*ey**2 + 6*jx**2 - 2*jy**2 + 8*E**4*(-1 + ey**2 + 8*ez**2 + 2*jx**2 + jy**2) + E**2*(-4 - 31*ey**2 + 32*ez**2 - 7*jx**2 + 9*jy**2)) - ey*(2*(7*ey**2 + jx**2 - jy**2) + 8*E**4*(-1 + ey**2 + 8*ez**2 + 4*jx**2 + jy**2) + E**2*(-4 - 31*ey**2 + 32*ez**2 + 11*jx**2 + 9*jy**2))*jz + ex**2*(-((14 + 45*E**2 + 160*E**4)*ez*jy) + 3*(14 - 27*E**2 + 16*E**4)*ey*jz) + 2*(-2 + 9*E**2 + 8*E**4)*ex*jx*(7*ey*ez + jy*jz)) + 3*E**3*(ez*jy*(-4 - 3*ey**2 + 32*ez**2 + 5*jx**2 + 5*jy**2) + ey*(4 + 3*ey**2 - 32*ez**2 - 15*jx**2 - 5*jy**2)*jz + ex**2*(-73*ez*jy + 3*ey*jz) + 10*ex*jx*(7*ey*ez + jy*jz))*np.arccos(-1.0/E)))/(32.*E**2*np.sqrt(ex**2 + ey**2 + ez**2))

        if args.verbose==True:
            print( 'Numerically integrated: Delta e = ',Delta_e,'; analytic expression: Delta e = ',Delta_e_an)

        N_r = 6
        assert round(Delta_e,N_r) == round(Delta_e_an,N_r)

        print("Test passed")
        
        code.reset()
        
        if HAS_MATPLOTLIB == True and args.plot==True:
            fig = pyplot.figure(figsize=(8,6))
            plot1 = fig.add_subplot(1,1,1)
            
            t_print_array = np.array(t_print_array)
            e_print_array = np.array(e_print_array)
            
            plot1.plot(t_print_array*1.0e-6,e_print_array, color='k')
            
            fontsize = 15
            plot1.set_ylabel("$e$",fontsize=fontsize)
            plot1.set_xlabel("$t/\mathrm{Myr}$",fontsize=fontsize)
            
            pyplot.show()
    
    def test15(self,args):
        print("Test flybys module: using analytic formulae")

        code = SecularMultiple()
        CONST_G = code.CONST_G
        
        ### binary orbit ###
        a = 1.0
        e = 0.1
        m1 = 1.0
        m2 = 0.8
        M_per = 1.0
        E = 2.0
        Q = 100.0
        INCL = 0.4*np.pi
        AP = 0.25*np.pi
        LAN = 0.25*np.pi
        
        masses = [m1,m2]
        m = m1 + m2
        particles = Tools.create_nested_multiple(2,masses, [a], [e], [INCL], [AP], [LAN])
        binary = particles[2]
                
        t_ref = 1.0e5 ### not actually used in this case, but needs to be specified for external particles

        external_particle = Particle(mass = M_per, is_binary=True, is_external=True, external_t_ref=t_ref, e=E, external_r_p = Q, INCL = 1.0e-10, AP = 1.0e-10, LAN = 1.0e-10)

        particles.append(external_particle)

        code = SecularMultiple()
        code.add_particles(particles)

        code.include_quadrupole_order_terms = True
        code.include_octupole_order_binary_pair_terms = True
        code.include_hexadecupole_order_binary_pair_terms = False
        code.include_dotriacontupole_order_binary_pair_terms = False
        
        code.apply_external_perturbation_assuming_integrated_orbits()
        Delta_e = binary.e-e

        ### compute analytic result (https://ui.adsabs.harvard.edu/abs/2019MNRAS.487.5630H/abstract) ###
        e_vec_hat,j_vec_hat = compute_e_and_j_hat_vectors(INCL,AP,LAN)
        e_vec = e_vec_hat*e
        j_vec = j_vec_hat*np.sqrt(1.0-e**2)
        ex = e_vec[0]
        ey = e_vec[1]
        ez = e_vec[2]
        jx = j_vec[0]
        jy = j_vec[1]
        jz = j_vec[2]

        eps_SA = (M_per/np.sqrt(m*(m+M_per)))*pow(a/Q,3.0/2.0)*pow(1.0 + E,-3.0/2.0)
        eps_oct = (a/Q)*(m1-m2)/((1.0+E)*m)
        Delta_e_an = (5*eps_SA*(np.sqrt(1 - E**(-2))*((1 + 2*E**2)*ey*ez*jx + (1 - 4*E**2)*ex*ez*jy + 2*(-1 + E**2)*ex*ey*jz) + 3*E*ez*(ey*jx - ex*jy)*np.arccos(-1.0/E)))/(2.*E*np.sqrt(ex**2 + ey**2 + ez**2))
        
        Delta_e_an += -(5*eps_oct*eps_SA*(np.sqrt(1 - E**(-2))*(ez*jy*(14*ey**2 + 6*jx**2 - 2*jy**2 + 8*E**4*(-1 + ey**2 + 8*ez**2 + 2*jx**2 + jy**2) + E**2*(-4 - 31*ey**2 + 32*ez**2 - 7*jx**2 + 9*jy**2)) - ey*(2*(7*ey**2 + jx**2 - jy**2) + 8*E**4*(-1 + ey**2 + 8*ez**2 + 4*jx**2 + jy**2) + E**2*(-4 - 31*ey**2 + 32*ez**2 + 11*jx**2 + 9*jy**2))*jz + ex**2*(-((14 + 45*E**2 + 160*E**4)*ez*jy) + 3*(14 - 27*E**2 + 16*E**4)*ey*jz) + 2*(-2 + 9*E**2 + 8*E**4)*ex*jx*(7*ey*ez + jy*jz)) + 3*E**3*(ez*jy*(-4 - 3*ey**2 + 32*ez**2 + 5*jx**2 + 5*jy**2) + ey*(4 + 3*ey**2 - 32*ez**2 - 15*jx**2 - 5*jy**2)*jz + ex**2*(-73*ez*jy + 3*ey*jz) + 10*ex*jx*(7*ey*ez + jy*jz))*np.arccos(-1.0/E)))/(32.*E**2*np.sqrt(ex**2 + ey**2 + ez**2))

        if args.verbose==True:
            print( 'SecularMultiple Delta e = ',Delta_e,'; analytic expression: Delta e = ',Delta_e_an)

        N_r = 8
        assert round(Delta_e,N_r) == round(Delta_e_an,N_r)

        print("Test passed")

        code.reset()

    def test16(self,args):
        print("Test spin-orbit terms in 2-body system")

        particles = Tools.create_nested_multiple(2,[1.0, 1.0], [1.0], [0.99], [0.01], [0.01], [0.01])
        binaries = [x for x in particles if x.is_binary == True]
        bodies = [x for x in particles if x.is_binary == False]

        for index,b in enumerate(bodies):
            
            
            if index==0:
                b.include_spin_orbit_1PN_terms = True
                b.spin_vec_x = 1.0
                b.spin_vec_y = 0.0
                b.spin_vec_z = 0.0
            if index==1:
                b.include_spin_orbit_1PN_terms = False
                b.spin_vec_x = 0.0
                b.spin_vec_y = 2.0
                b.spin_vec_z = 0.0

        code = SecularMultiple()
        code.add_particles(particles)

        # Theoretical prediction #
        CONST_G = code.CONST_G
        CONST_C = code.CONST_C
        a = binaries[0].a
        e = binaries[0].e
        m1 = bodies[0].mass
        m2 = bodies[1].mass
        M = binaries[0].mass
        rg = CONST_G*M/(CONST_C**2)
        P = 2.0*np.pi*np.sqrt(a**3/(CONST_G*M))
        t_1PN = (1.0/3.0)*P*(1.0-e**2)*(a/rg)
        mu = m1*m2/M
        L = mu*np.sqrt(CONST_G*M*a*(1.0-e**2))
        omega_deSitter = 2.0*CONST_G* ((1.0 + (3.0/4.0)*m2/m1)/(CONST_C**2*a**3*pow(1.0-e**2,3.0/2.0))) * L
        t_deSitter = 2.0*np.pi/omega_deSitter
        
        t = 0.0
        N=1000
        tend = t_deSitter ### integrate for exactly one precession timescale
        dt=tend/float(N)

        t_print_array = []
        a_print_array = []
        e_print_array = []
        AP_print_array = []
        Sx_print_array = [[] for x in range(len(bodies))]
        Sy_print_array = [[] for x in range(len(bodies))]
        Sz_print_array = [[] for x in range(len(bodies))]
        S_print_array = [[] for x in range(len(bodies))]

        while (t<tend):
            t+=dt
            code.evolve_model(t)

            if args.verbose==True:
                print( 't/Myr',t,'Sx',[b.spin_vec_x for b in bodies],'Sy',[b.spin_vec_y for b in bodies],'Sz',[b.spin_vec_z for b in bodies])
            t_print_array.append(t)
            a_print_array.append(binaries[0].a)
            e_print_array.append(binaries[0].e)
            AP_print_array.append(binaries[0].AP)
            for index,b in enumerate(bodies):
                S_print_array[index].append( np.sqrt( b.spin_vec_x**2 + b.spin_vec_y**2 + b.spin_vec_z**2) )
                Sx_print_array[index].append(b.spin_vec_x)
                Sy_print_array[index].append(b.spin_vec_y)
                Sz_print_array[index].append(b.spin_vec_z)
        
        t_print_array = np.array(t_print_array)
        a_print_array = np.array(a_print_array)
        e_print_array = np.array(e_print_array)
        AP_print_array = np.array(AP_print_array)
        

        ### Since the integration time is exactly one precession timescale, the final spins should be equal to the initial ones; at half the integration time, they should be equal to minus the initial ones ###
        assert round(Sx_print_array[0][-1],4) == round(Sx_print_array[0][0],4)
        assert round(Sx_print_array[0][500],4) == -round(Sx_print_array[0][0],4)
        print("Test passed")

        code.reset()
                
        if HAS_MATPLOTLIB == True and args.plot==True:
            fig = pyplot.figure(figsize=(16,10))
            plot1 = fig.add_subplot(2,1,1)

            for index in range(len(bodies)):
                plot1.plot(t_print_array*1.0e-6,S_print_array[index], color='k',label="$S$")
                plot1.plot(t_print_array*1.0e-6,Sx_print_array[index], color='r',label="$S_x$")
                plot1.plot(t_print_array*1.0e-6,Sy_print_array[index], color='g',label="$S_y$")
                plot1.plot(t_print_array*1.0e-6,Sz_print_array[index], color='b',label="$S_z$")

            fontsize = 15
            plot1.set_xlabel("$t/\mathrm{Myr}$",fontsize=fontsize)
            plot1.set_ylabel("$S$",fontsize=fontsize)
            
            handles,labels = plot1.get_legend_handles_labels()
            plot1.legend(handles,labels,loc="upper left",fontsize=0.6*fontsize)

            pyplot.show()


    def test17(self,args):
        print("Test stationary eccentricity root finding")

        particles = Tools.create_nested_multiple(3, [1.0,1.0e-3,40.0e-3],[6.0,100.0],[0.001,0.6],[0.0,65.0*np.pi/180.0],[45.0*np.pi/180.0,0.0],[0.0,0.0])
        binaries = [x for x in particles if x.is_binary==True]
        
        code = SecularMultiple()
        code.add_particles(particles)
        inner_binary = binaries[0]
        outer_binary = binaries[1]
        
        inner_binary.check_for_stationary_eccentricity = True
        
        e_print = []
        INCL_print = []
        rel_INCL_print = []
        t_print = []
        
        start = time.time()
    
        t = 0.0
        N = 1000
        tend = 3.0e6
        t_print_indices_min = []
        t_print_indices_max = []

        i_print = 0
        dt = tend/float(N)
        while t<=tend:
            t+=dt
            code.evolve_model(t)
            t = code.model_time
            flag = code.flag
            
            if args.verbose==True:
                print( 't',t,'es',[x.e for x in binaries],'INCL_parent',inner_binary.INCL_parent,"flag",flag,"max e",[x.maximum_eccentricity_has_occurred for x in binaries],"min e",[x.minimum_eccentricity_has_occurred for x in binaries])

            rel_INCL_print.append(inner_binary.INCL_parent)
            e_print.append(inner_binary.e)
            INCL_print.append(inner_binary.INCL)
            t_print.append(t)
            i_print += 1
        
            if flag==2:
                if inner_binary.minimum_eccentricity_has_occurred == True:
                    t_print_indices_min.append(i_print-1)
                if inner_binary.maximum_eccentricity_has_occurred == True:
                    t_print_indices_max.append(i_print-1)

                inner_binary.minimum_eccentricity_has_occurred = False
                inner_binary.maximum_eccentricity_has_occurred = False

                ### Integrate for a short time without stationary eccentricity root finding, to avoid "getting stuck" and finding the same stationary point over and over again. ###
                inner_binary.check_for_stationary_eccentricity = False
                code.evolve_model(t+dt)
                t=code.model_time
                inner_binary.check_for_stationary_eccentricity = True
                
            
        if args.verbose==True:
            print('wall time',time.time()-start)
        
        t_print = np.array(t_print)
        rel_INCL_print = np.array(rel_INCL_print)
        e_print = np.array(e_print)
        
        ### Check times of first maximum and minimum ###
        Nr = 1
        assert(round(t_print[t_print_indices_max[0]],Nr) == 577762.4)
        assert (round(t_print[t_print_indices_min[0]],Nr) == 836755.1)

        print("Test passed")

        code.reset()
                
        if HAS_MATPLOTLIB==True and args.plot==True:
            fig=pyplot.figure()
            plot1=fig.add_subplot(2,1,1)
            plot2=fig.add_subplot(2,1,2,yscale="log")
            plot1.plot(1.0e-6*t_print,rel_INCL_print*180.0/np.pi)
            plot2.plot(1.0e-6*t_print,1.0-e_print)
            
            plot1.scatter(1.0e-6*t_print[t_print_indices_min],rel_INCL_print[t_print_indices_min]*180.0/np.pi,color='b',label="$\mathrm{Local\,minima}$")
            plot1.scatter(1.0e-6*t_print[t_print_indices_max],rel_INCL_print[t_print_indices_max]*180.0/np.pi,color='r',label="$\mathrm{Local\,maxima}$")

            plot2.scatter(1.0e-6*t_print[t_print_indices_min],1.0-e_print[t_print_indices_min],color='b',label="$\mathrm{Local\,}e_\mathrm{in}\mathrm{-minima}$")
            plot2.scatter(1.0e-6*t_print[t_print_indices_max],1.0-e_print[t_print_indices_max],color='r',label="$\mathrm{Local\,}e_\mathrm{in}\mathrm{-maxima}$")
            
            plot2.set_xlabel("$t/\mathrm{Myr}$")
            plot1.set_ylabel("$i_\mathrm{rel}/\mathrm{deg}$")
            plot2.set_ylabel("$1-e_\mathrm{in}$")
            
            handles,labels = plot2.get_legend_handles_labels()
            plot2.legend(handles,labels,loc="best",fontsize=12)

            pyplot.show()

def compute_e_and_j_hat_vectors(INCL,AP,LAN):
    sin_INCL = np.sin(INCL)
    cos_INCL = np.cos(INCL)
    sin_AP = np.sin(AP)
    cos_AP = np.cos(AP)
    sin_LAN = np.sin(LAN)
    cos_LAN = np.cos(LAN)
    
    e_hat_vec_x = (cos_LAN*cos_AP - sin_LAN*sin_AP*cos_INCL);
    e_hat_vec_y = (sin_LAN*cos_AP + cos_LAN*sin_AP*cos_INCL);
    e_hat_vec_z = (sin_AP*sin_INCL);
    
    j_hat_vec_x = sin_LAN*sin_INCL;
    j_hat_vec_y = -cos_LAN*sin_INCL;
    j_hat_vec_z = cos_INCL;

    e_hat_vec = np.array([e_hat_vec_x,e_hat_vec_y,e_hat_vec_z])
    j_hat_vec = np.array([j_hat_vec_x,j_hat_vec_y,j_hat_vec_z])

    return e_hat_vec,j_hat_vec
    
if __name__ == '__main__':
    args = parse_arguments()
    
    N_tests = 17
    if args.test==0:
        tests = range(1,N_tests+1)
    else:
        tests = [args.test]

    t=test_secularmultiple()
    for i in tests:
        print( 'Running test number',i,'; verbose =',args.verbose,'; plot =',args.plot)
        function = getattr(t, 'test%s'%i)
        function(args)
    
    print("="*50)
    print("All tests passed!")
