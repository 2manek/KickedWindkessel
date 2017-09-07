# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 21:13:26 2017

@author: teos
"""
import numpy as np
from scipy.integrate import ode
import pdb

""" 
  C_a{dp_a}/{dt}=\sum_{i} \delta(t-t_i)Z_{ca}(p_c-p_I)	- Z_{av}p_{av}
  C_c{dp_c}/{dt}=max(Z_{vc}p_{vc},0) - \sum_{i} \delta(t-t_i)Z_{ca}(p_c-p_I)	
  C_v{dp_v}/{dt}= Z_{av}p_{av} - max(Z_{vc}p_{vc},0)
  p_I(t)=p_{I0}+p_{I1}(1+cos\:2\pi\Phi(t))  
\end{equation}	
\begin{equation}	
	d \phi/dt=1/T_0+\sum_{j} \delta(t-t_j-\tau)F(\tilde{\varphi})/T_{RSA}
\end{equation}	
\begin{equation}	
	d \Phi/dt=1/T_{R0}
\end{equation}
\begin{equation}	
	t_i:\varphi(t_i)=i, \tilde{\varphi} = \varphi\:mod\:1
\end{equation}	
\begin{equation}	
	t_j:\Phi(t_j)=j
\end{equation}
\begin{equation}	
	F(\varphi)=\varphi^{1.3}(\varphi-0.45)\frac{(1-\varphi)^3}{(1-0.8)^3+(1-\varphi)^3}
\end{equation}	
     """
class HeartActionForce:
    def __init__(self):
        self.Drive = 0.0
        self.CoordinateNumber = 0
    def UpdateDrive(self,data):
        pass

class  RungeKutta45IntegratorParams:
            def __init__(self):
                self.dimension = 0
                self.Tmin = 0
                self.dT = 0
                self.Npoints = 0

class RungeKutta45ConstStepIntegrator:

    def __init__(self,param,function,data):
        self.Force = 0.0
        self.CoordinateNumber = 0
        self.param = param
        self.function = function
        self.endTime = self.param.Tmin  + self.param.Tdelta * self.param.Npoints
        self.data = data        
        
    def Reset(self,param):        
        self.param = param
        self.endTime = self.param.Tmin  + self.param.Tdelta * self.param.Npoints        
        # create explicit Runge-Kutta integrator of order (4)5
        self.r = ode(self.function).set_integrator('dopri5')
        #pdb.set_trace()
        self.r.set_initial_value(self.data.y, self.param.Tmin)
        

    def Iterate(self):
        if not self.r.successful():
            return False
        self.data.t = self.data.t + self.param.Tdelta
        #print("Przed %s" % self.data.y)
        self.data.y = self.r.integrate(self.data.t)
        #print("Po %s" % self.data.y)
        return self.data.t < self.endTime
    class  RungeKutta45IntegratorData:
            def __init__(self,param = RungeKutta45IntegratorParams()):
                self.dimension = param.dimension
                self.y =  [0 for x in range(self.dimension)]
                self.t = param.Tmin
            def __str__(self):
                return "%lf,%s"%(self.t,','.join([str(x) for x in self.y]))
            def __getitem__(self, index):
                result = self.y.__getitem__(index)
                return result          
            def __setitem__(self, index,value):
                result = self.y.__setitem__(index,value)
                return result                  
    
        # Place your FUNCTION HERE
def f(t,y,settings):
            """definition of equation-example
            damped harmonic oscillator with harmonic driver
            x" + 100*x + 2*x'= 10*sin 3*t
            we define y[0] = x, y[1] = x'
            You need to transform the second order differential equation
            in a system of two differential equatios of first order:
            f[0] = x'= y[1]
            f[1] = x" = -100*x-2*x' = -100 *y[0] -2*y[1] + 10*sin 3*t
            You may enter your own equation here!"""
            #pdb.set_trace()
            #print(y)
            Freturn = y
            #print(len(y))
            p_a, p_c, p_v, p_I,dummy = y
            #print("p_a %lf p_c %lf p_v %lf p_I %lf" % (p_a, p_c, p_v, p_I))
            if settings.openHeartFlow > 0.0: # //open the heart flow            
                if settings.heartFlowBeginTime == -1:                
                    settings.lastDiastolicBp = p_a #; //register diastolic on opening.                
                settings.heartFlowBeginTime = t
                settings.lastHeartBeatTime = t
                                

            heartFlowIsOpen = (settings.heartFlowBeginTime >= 0.0)#;//ok, it holds the real time: the flow is open.
            #//check if it should not be closed
            openTime = t - settings.heartFlowBeginTime
            if heartFlowIsOpen and (openTime > settings.heartFlowTimespan):
                settings.heartFlowBeginTime = -1.0#; //self parameter is set to current time when flow opens. When the flow is closed, it is set to a negative value.
                #//register systolic on closing.
                #//settings.lastSystolicBp = p_a; //close the heart: register systolic now
                heartFlowIsOpen = False
            
            #//Fs = 125; time step = 1/125 s
            q_ca = settings.Zca * (p_c - p_I)
            if not heartFlowIsOpen:
                q_ca = 0.0
            q_vc = np.max(settings.Zvc * (p_v - p_c), 0.0)
            q_av = settings.Zav * (p_a - p_v)
            Freturn[0] = (q_ca - q_av) / settings.Ca#; //p_a : //C_a{dp_a}/{dt}=\sum_{i} \delta(t-t_i)Z_{ca}(p_c-p_I)	- Z_{av}p_{av}
            Freturn[1] = (q_vc - q_ca) / settings.Cc#;//p_c : //  C_c{dp_c}/{dt}=max(Z_{vc}p_{vc},0) - \sum_{i} \delta(t-t_i)Z_{ca}(p_c-p_I)	
            Freturn[2] = (q_av - q_vc) / settings.Cv#;//p_v // //  C_v{dp_v}/{dt}= Z_{av}p_{av} - max(Z_{vc}p_{vc},0)
            #//non-autonomous
            Freturn[3] = settings.p_I0 + settings.p_I1 * (1 + np.cos(2 * np.pi * t / settings.breathingPeriod)) - p_I#;//p_I : //  p_I(t)=p_{I0}+p_{I1}(1+cos\:2\pi\Phi(t))                          
            #print(Freturn)
            y = Freturn
            #pdb.set_trace()
            
            return Freturn
        #//p_a = y[0]
        #//p_c = y[1]
        #//p_v = y[2]
        #//p_I = y[3]
        #//F(\varphi)=\varphi^{1.3}(\varphi-0.45)\frac{(1-\varphi)^3}{(1-0.8)^3+(1-\varphi)^3}
    
class KickedWindkesselModel:
        class KickedWindkesselModelSettings:
 
            def __init__(self):            
                self.lastHeartBeatTime = 0.0;
                self.lastDiastolicBp = 0.0;
                self.lastSystolicBp = 0.0;
            
                #bp
                #Rav=0.9;%th(16);%1
                #Rbv=0.005;%0.0005;%0.01;%0.01;%0.01;%th(20);%0.01
                #Rba=0.006;%0.0029;%0.0029;%0.003;%th(15);%0.006

                #Cb=th(7);%4.3
                #Ca=th(3);%1.6
                #Cv=th(4);%100
                self.Ca = 1.6
                self.Cc = 4.3
                self.Cv = 100.0
                self.Zca = 1 / 0.006
                self.Zav = 1 / 0.9
                self.Zvc = 1 / 0.005
                #breathing
                self.p_I0 = -4.0
                self.p_I1 = 0.1
                self.breathingPeriod = 3.0
                self.heartPhase = 0.0
                #self.heartActionForce = NullDrivingForce()
                #//with time_multiplier 30 the asymptotic HR as function of e is around 207 bbm
                #//time_multiplier 40 HRasympt = 155 BPM
                #//time_multiplier 50 HRasympt = 122 BPM                
                self.heartFlowTimespan = 0.01#;//0.1 sec
                self.throwAmplitudeDeathException = False
                self.heartFlowBeginTime = -1
                self.openHeartFlow = 0.0
            
            def KickedWindkesselModelSettings(self,settings):   
                self.lastHeartBeatTime = 0.0;
                self.lastDiastolicBp = 0.0;
                self.lastSystolicBp = 0.0;
            
                #bp
                #Rav=0.9;%th(16);%1
                #Rbv=0.005;%0.0005;%0.01;%0.01;%0.01;%th(20);%0.01
                #Rba=0.006;%0.0029;%0.0029;%0.003;%th(15);%0.006

                #Cb=th(7);%4.3
                #Ca=th(3);%1.6
                #Cv=th(4);%100
                self.Ca = 1.6
                self.Cc = 4.3
                self.Cv = 100.0
                self.Zca = 1 / 0.006
                self.Zav = 1 / 0.9
                self.Zvc = 1 / 0.005
                #breathing
                self.p_I0 = -4.0
                self.p_I1 = 0.1
                self.breathingPeriod = 3.0
                self.heartPhase = 0.0
              
                self.heartFlowTimespan = 0.01#;//0.1 sec
                self.throwAmplitudeDeathException = False
                self.heartFlowBeginTime = -1
                self.openHeartFlow = 0.0
                
                self.breathingPeriod = settings.breathingPeriod
                self.Ca = settings.Ca
                self.Cc = settings.Cc
                self.Cv = settings.Cv
                self.heartPhase = settings.heartPhase
                self.openHeartFlow = settings.openHeartFlow
                self.p_I0 = settings.p_I0
                self.p_I1 = settings.p_I1
                self.Zav = settings.Zav
                self.Zca = settings.Zca
                self.Zvc = settings.Zvc
                self.throwAmplitudeDeathException = settings.throwAmplitudeDeathException
                self.heartFlowBeginTime = settings.heartFlowBeginTime
                self.heartFlowTimespan = settings.heartFlowTimespan
                self.heartActionForce = settings.heartActionForce

            

        def phaseEfectivenessCurve(phi):        
            aux1 = np.power(1 - phi, 3.0)
            value = np.power(phi, 1.3) * (phi - 0.45) * (aux1 / ((np.power(1 - 0.8, 3.0)) + aux1));
            return value
        
        @property
        def ModelDimension(self):
                return 5
                
        def __init__(self,settings):                    
            self.settings = settings#;// new KickedWindkesselModelSettings(settings);
            self.param = RungeKutta45IntegratorParams()
            self.param.dimension = self.ModelDimension
            self.param.Tdelta = 0.01#;//1/100 or 1/125 //ol = 2 * 1E-7;                    //error control tolerance
            self.param.Tmin = 0.0#                         //startpoint
            self.param.Npoints = 10000#
            self.data = RungeKutta45ConstStepIntegrator.RungeKutta45IntegratorData(self.param)
            #//initialize
            self.data[0] = 90.0#;//P(2) = 90;%Pa 90
            self.data[1] = 35.0#;//P(1) = 35;%25;%95;%Pb
            self.data[2] = 45.0#;//P(3) = 45;%35;%70;%Pv % bylo 30 i zle asymtotyczni    
            self.data[3] = settings.p_I0#;
            self.data[4] = 0#;
            
            self.integrator = RungeKutta45ConstStepIntegrator(self.param,lambda t,y: f(t,y,self.settings),self.data)
            

        @property
        def Npoints(self):
                return self.param.Npoints

        @Npoints.setter
        def Npoints(self, value):
            self.param.Npoints = value            
            
        @property
        def BeginTime(self):
                return self.param.Tmin

        @BeginTime.setter
        def BeginTime(self, value):
            self.param.Tmin = value

        @property
        def EndTime(self):
                return self.param.Tmin  + self.param.Tdelta * self.param.Npoints


        @property
        def TimeDelta(self):
                return self.param.Tdelta

        @TimeDelta.setter
        def TimeDelta(self, value):
            self.param.Tdelta = value

        @property
        def Dimension(self):
                return self.param.dimension


        @property
        def InitialConditions(self):
                return self.data.y

        @InitialConditions.setter
        def InitialConditions(self, value):
            self.data.y = value

        @property
        def IntegratorData(self):
                return self.data

        @IntegratorData.setter
        def ids(self, value):
            self.data = value


        def IterateToNotifiers(self):
            #print("IterateToNotifiers: %d" % self.param.Npoints)
            self.integrator.Reset(self.param)#;//actualize parameters
            while True:            
                #self.settings.heartActionForce.UpdateDrive(self.data)
                #self.data[self.settings.heartActionForce.CoordinateNumber] = self.settings.heartActionForce.Drive
                self.settings.openHeartFlow = self.settings.heartActionForce.Drive
                isHeartOpen = (self.settings.heartFlowBeginTime != -1.0)
                self.settings.sineOfBreathingPhase = np.sin(2 * np.pi * self.data.t / self.settings.breathingPeriod)
                if isHeartOpen:                
                    abc = 1
                
                if not self.integrator.Iterate():
                    break
                isHeartClosedAfter = (self.settings.heartFlowBeginTime == -1.0)
                if  isHeartOpen and isHeartClosedAfter: #//it has just closed.                
                    self.settings.lastSystolicBp = self.data[0]                
                if self.settings.throwAmplitudeDeathException:
                    if self.data[0] < 0.0:
                        raise Exception("Amplitude death occurred")
                self.Notify(self.data)

def NotifyPlainPrint(data):
    print(str(data))

def DummyPrint(data):
    pass
if __name__ == "__main__":
    settings = KickedWindkesselModel.KickedWindkesselModelSettings()    
    settings.heartActionForce = HeartActionForce()
    model = KickedWindkesselModel(settings)
    model.param.Npoints = 10
    model.Notify = NotifyPlainPrint
    #model.Notify = DummyPrint
    model.IterateToNotifiers()
