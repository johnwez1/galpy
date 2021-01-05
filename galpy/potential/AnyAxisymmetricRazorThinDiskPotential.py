###############################################################################
#   AnyAxisymmetricRazorThinDiskPotential.py: class that implements the
#                                             potential of an arbitrary
#                                             axisymmetric, razor-thin disk
###############################################################################
import numpy
from scipy import integrate, special
from .Potential import Potential
class AnyAxisymmetricRazorThinDiskPotential(Potential):
    """Class that implements the potential of an arbitrary axisymmetric, razor-thin disk with surface density :math:`\Sigma(R)`"""
    def __init__(self,surfdens=lambda R: 1.5*numpy.exp(-R/0.3),amp=1.,
                 ro=None,vo=None):
        """
        NAME:

           __init__

        PURPOSE:

           Initialize the potential of an arbitrary axisymmetric disk

        INPUT:

           amp= (1.) amplitude to be applied to the potential

           surfdens= (1.5 e^[-R/0.3]) function of a single variable that gives the surface density as a function of radius (can return a Quantity)

           ro=, vo= distance and velocity scales for translation into internal units (default from configuration file)

        OUTPUT:

           AnyAxisymmetricRazorThinDiskPotential object

        HISTORY:

           2021-01-04 - Written - Bovy (UofT)

        """
        Potential.__init__(self,amp=amp,ro=ro,vo=vo)
        self._sdens= surfdens
        self._pot_zero= -2.*numpy.pi*integrate.quad(lambda a: self._sdens(a),
                                                    0,numpy.inf)[0]

    def _evaluate(self,R,z,phi=0.,t=0.):
        """
        NAME:
           _evaluate
        PURPOSE:
           evaluate the potential at (R,z)
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth
           t - time
        OUTPUT:
           potential at (R,z)
        HISTORY:
           2021-01-04 - Written - Bovy (UofT)
        """
        if R == 0 and z == 0:
            return self._pot_zero
        elif numpy.isinf(R**2+z**2):
            return 0.
        potint= lambda a: a*self._sdens(a)\
           /numpy.sqrt((R+a)**2.+z**2.)*special.ellipk(4*R*a/((R+a)**2.+z**2.))
        return -4*(integrate.quad(potint,0,2*R,points=[R])[0]
                   +integrate.quad(potint,2*R,numpy.inf)[0])
    
    def _Rforce(self,R,z,phi=0.,t=0.):
        """
        NAME:
           _Rforce
        PURPOSE:
           evaluate the radial force at (R,z)
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth
           t - time
        OUTPUT:
           F_R at (R,z)
        HISTORY:
           2021-01-04 - Written - Bovy (UofT)
        """
        R2= R**2
        z2= z**2
        def rforceint(a):
            a2= a**2
            aRz= (a+R)**2.+z2
            faRoveraRz= 4*a*R/aRz
            return a*self._sdens(a)\
                *((a2-R2+z2)*special.ellipe(faRoveraRz)
                  -((a-R)**2+z2)*special.ellipk(faRoveraRz))\
                  /R/((a-R)**2+z2)/numpy.sqrt(aRz)
        return 2*(integrate.quad(rforceint,0,2*R,points=[R])[0]
                  +integrate.quad(rforceint,2*R,numpy.inf)[0])

    def _zforce(self,R,z,phi=0.,t=0.):
        """
        NAME:
           _zforce
        PURPOSE:
           evaluate the vertical force at (R,z)
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth
           t - time
        OUTPUT:
           F_z at (R,z)
        HISTORY:
           2021-01-04 - Written - Bovy (UofT)
        """
        if z == 0:
            return 0.
        z2= z**2
        def zforceint(a):
            aRz= (a+R)**2.+z2
            faRoveraRz= 4*a*R/aRz
            return a*self._sdens(a)\
                *special.ellipe(faRoveraRz)/((a-R)**2+z2)/numpy.sqrt(aRz)
        return -4*z*(integrate.quad(zforceint,0,2*R,points=[R])[0]
                     +integrate.quad(zforceint,2*R,numpy.inf)[0])
    
    def _R2deriv(self,R,z,phi=0.,t=0.):
        """
        NAME:
           _R2deriv
        PURPOSE:
           evaluate the 2nd radial derivative at (R,z)
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth
           t - time
        OUTPUT:
           d2 Phi / dR2 at (R,z)
        HISTORY:
           2021-01-04 - Written - Bovy (UofT)
        """
        R2= R**2
        z2= z**2
        def r2derivint(a):
            a2= a**2
            aRz= (a+R)**2.+z2
            faRoveraRz= 4*a*R/aRz
            return a*self._sdens(a)\
                *(-(((a2-3.*R2)*(a2-R2)**2+(3.*a2**2+2.*a2*R2+3.*R2**2)*z2
                    +(3.*a2+7.*R2)*z**4+z**6)*special.ellipe(faRoveraRz))
                 +((a-R)**2+z2)*((a2-R2)**2+2.*(a2+2.*R2)*z2+z**4)
                 *special.ellipk(faRoveraRz))\
                 /(2.*R2*((a-R)**2+z2)**2*((a+R)**2+z2)**1.5)
        return -4*(integrate.quad(r2derivint,0,2*R,points=[R])[0]
                  +integrate.quad(r2derivint,2*R,numpy.inf)[0])

    def _z2deriv(self,R,z,phi=0.,t=0.):
        """
        NAME:
           _z2deriv
        PURPOSE:
           evaluate the 2nd vertical derivative at (R,z)
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth
           t - time
        OUTPUT:
           d2 Phi / dz2 at (R,z)
        HISTORY:
           2021-01-04 - Written - Bovy (UofT)
        """
        R2= R**2
        z2= z**2
        def z2derivint(a):
            a2= a**2
            aRz= (a+R)**2.+z2
            faRoveraRz= 4*a*R/aRz
            return a*self._sdens(a)\
                *(-(((a2-R2)**2-2.*(a2+R2)*z2-3.*z**4)*special.ellipe(faRoveraRz))
                  -z2*((a-R)**2+z2)*special.ellipk(faRoveraRz))\
                  /(((a-R)**2+z2)**2*((a+R)**2+z2)**1.5)
        return -4*(integrate.quad(z2derivint,0,2*R,points=[R])[0]
                  +integrate.quad(z2derivint,2*R,numpy.inf)[0])

    def _Rzderiv(self,R,z,phi=0.,t=0.):
        """
        NAME:
           _Rzderiv
        PURPOSE:
           evaluate the mixed radial, vertical derivative at (R,z)
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth
           t - time
        OUTPUT:
           d2 Phi / dRdz at (R,z)
        HISTORY:
           2021-01-04 - Written - Bovy (UofT)
        """
        R2= R**2
        z2= z**2
        def rzderivint(a):
            a2= a**2
            aRz= (a+R)**2.+z2
            faRoveraRz= 4*a*R/aRz
            return a*self._sdens(a)\
                *(-((a**4-7.*R**4-6.*R2*z2+z**4+2.*a2*(3.*R2+z2))
                   *special.ellipe(faRoveraRz))
                 +((a-R)**2+z**2)*(a2-R2+z2)*special.ellipk(faRoveraRz))\
                 /R/((a-R)**2+z2)**2/((a+R)**2+z2)**1.5
        return -2*z*(integrate.quad(rzderivint,0,2*R,points=[R])[0]
                  +integrate.quad(rzderivint,2*R,numpy.inf)[0])

    def _surfdens(self,R,z,phi=0.,t=0.):
        """
        NAME:
           _surfdens
        PURPOSE:
           evaluate the surface density
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth
           t - time
        OUTPUT:
           Sigma (R,z)
        HISTORY:
           2021-01-04 - Written - Bovy (UofT)
        """
        return self._sdens(R)
