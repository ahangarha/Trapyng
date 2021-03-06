"""
In this document we download we want to visualize the data
and be able to play around with different distributions in 2D.
Visualizing the original data, the clusters, responsibilities,
and responsibilities through time.
"""

import os
os.chdir("../../")
import import_folders
# Classical Libraries
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import copy as copy
# Data Structures Data
import CPortfolio as CPfl

# Own graphical library
from graph_lib import gl 
# Import functions independent of DataStructure
import utilities_lib as ul
# For statistics. Requires statsmodels 5.0 or more
# Analysis of Variance (ANOVA) on linear models
import basicMathlib as bMA

import DDBB_lib as DBl

import CEM as CEM 
import CDistribution as Cdist

import specific_plotting_func as spf

gl.close("all")

##############################################
########## FLAGS ############################
trading_graph = 0
perform_EM = 1
perform_HMM_after_EM = 1

final_clusters_graph = 1
responsibility_graph = 1
##########################################################################
################# DATA OBTAINING ######################################
##########################################################################
######## SELECT SOURCE ########
dataSource =  "Google"  # Hanseatic  FxPro GCI Yahoo
[storage_folder, info_folder, 
 updates_folder] = ul.get_foldersData(source = dataSource)
folder_images = "../pics/Trapying/EM_trading/"
ul.create_folder_if_needed(folder_images)

######## SELECT SYMBOLS AND PERIODS ########
symbols = ["XAUUSD","Mad.ITX", "EURUSD"]
symbols = ["Alcoa_Inc"]
symbols = ["GooG", "Alcoa_Inc"]
periods = [5]

# Create porfolio and load data
cmplist = DBl.read_NASDAQ_companies(whole_path = "../storage/Google/companylist.csv")
cmplist.sort_values(by = ['MarketCap'], ascending=[0],inplace = True)
symbolIDs = cmplist.iloc[0:30]["Symbol"].tolist()

symbol_ID_indx1 = 0
symbol_ID_indx2 = 1

for period in periods:
    Cartera = CPfl.Portfolio("BEST_PF", symbolIDs, [period]) 
    Cartera.set_csv(storage_folder)
    
sdate = dt.datetime.strptime("1-8-2017", "%d-%m-%Y")
edate = dt.datetime.strptime("15-9-2017", "%d-%m-%Y")
#edate = dt.datetime.now()

Cartera.set_interval(sdate, edate)

opentime, closetime = Cartera.get_timeData(symbolIDs[symbol_ID_indx1],periods[0]).guess_openMarketTime()
dataTransform = ["intraday", opentime, closetime]


######### FILL THE DATA #####################
## TODO: How are we filling the data ? 

fill_data_f = 0
if (fill_data_f):
    Cartera.get_timeData(symbolIDs[symbol_ID_indx1],periods[0]).fill_data()
    Cartera.get_timeData(symbolIDs[symbol_ID_indx2],periods[0]).fill_data()

########## Obtain the data ###############
ret1 = Cartera.get_timeData(symbolIDs[symbol_ID_indx1],periods[0]).get_timeSeriesReturn()*100
ret2 = Cartera.get_timeData(symbolIDs[symbol_ID_indx2],periods[0]).get_timeSeriesReturn()*100

dates = Cartera.get_timeData(symbolIDs[symbol_ID_indx1],periods[0]).get_dates()
dates2 = Cartera.get_timeData(symbolIDs[symbol_ID_indx2],periods[0]).get_dates()

symbolIDs = cmplist.iloc[0:30]["Symbol"].tolist()

symbol_ID1 = symbolIDs[symbol_ID_indx1]
symbol_ID2 = symbolIDs[symbol_ID_indx2]

#print dates[0], dates[26], dates[27]
################# Plotting the data #################
if(trading_graph):
    
    # Trading plot of the points !

    title = "CLOSE Price, Volume and Return evolution"
    
    ax1 = gl.subplot2grid((4,1), (0,0), rowspan=1, colspan=1) 
    gl.tradingBarChart(Cartera.get_timeData(symbolIDs[symbol_ID_indx1],periods[0]), ax = ax1,
                             dataTransform = dataTransform, AxesStyle = "Normal - No xaxis", color = "k",
                             labels = [title,"",symbolIDs[symbol_ID_indx1] +"(" +str(periods[0])+"M)"])
    
    ax2 = gl.subplot2grid((4,1), (1,0), rowspan=1, colspan=1, sharex = ax1) 
    gl.tradingBarChart(Cartera.get_timeData(symbolIDs[symbol_ID_indx2],periods[0]), ax = ax2,
                             dataTransform = dataTransform, AxesStyle = "Normal - No xaxis", color = "k",
                             labels = ["","",symbolIDs[symbol_ID_indx2] +"(" +str(periods[0])+"M)"])

    ax3 = gl.subplot2grid((4,1), (2,0), rowspan=1, colspan=1) 
    gl.stem(dates, ret1, ax = ax3, dataTransform = dataTransform,
                   AxesStyle = "Normal",
                   labels = ["","",symbolIDs[symbol_ID_indx1] +"("+ str(periods[0])+ "M)"], legend = ["Return"])
    
    ax4 = gl.subplot2grid((4,1), (3,0), rowspan=1, colspan=1, sharex = ax1, sharey = ax3) 
    gl.stem(dates, ret2, ax = ax4, dataTransform = dataTransform,
                   AxesStyle = "Normal",
                   labels = ["","",symbolIDs[symbol_ID_indx2] +"("+ str(periods[0])+ "M)"], legend = ["Return"])
#    
    gl.set_fontSizes(ax = [ax1,ax2,ax3,ax4], title = 20, xlabel = 20, ylabel = 20, 
                      legend = 20, xticks = 10, yticks = 10)
    
    gl.subplots_adjust(left=.09, bottom=.10, right=.90, top=.95, wspace=.01, hspace=0.01)

    gl.savefig(folder_images +'PriceAndReturns2Symbol_EM.png', 
               dpi = 100, sizeInches = [22, 12])
    
##########################################################################
################# PREPROCESS DATA ######################################
##########################################################################

## Set GAP return as NAN

remove_gap_return = 1
if (remove_gap_return):
    """ We usually would like to remove the return of gaps if we are dealing
        with intraday data since they are ouliers for this distribution,
        they belong to a distribution with more time
    """
    # If we had all the data properly this would do.
    if(0):
        gap_ret = np.where(dates.time == opentime)[0]
    else:
    # If we do not, we need to find the first sample of each day.
        days_keys, day_dict = Cartera.get_timeData(symbolIDs[symbol_ID_indx1],periods[0]).get_indexDictByDay()
        gap_ret = [day_dict[k][0] for k in days_keys]
#    print ("Indexes: ",day_dict[days_keys[0]])
    
    ret1[gap_ret,:] = np.NaN
    ret2[gap_ret,:] = np.NaN


    ## Remove the NaNs
    NonNan_index =  np.logical_not(np.isnan(ret1) | np.isnan(ret2))
    ret1 = ret1[NonNan_index[:,0],:]
    ret2 = ret2[NonNan_index[:,0],:]
    dates = dates[NonNan_index[:,0]]

#### Apply some shifting if we want crosscorrelations though time
lag_sigmals = 0
if(lag_sigmals != 0 ):
    ret2 = np.concatenate([ret2[lag_sigmals:,:], np.zeros((lag_sigmals,1))], axis = 0)
#    lag_sigmals = ret1[:-lag_sigmals,:]
    
## Final data

data = np.concatenate((ret1,ret2),axis = 1)
mean = np.mean(data, axis = 0)
corr = bMA.get_corrMatrix(data)
cov = bMA.get_covMatrix(data)

############################################################
################# PLOT DATA ###############################
############################################################

if (perform_EM):
#    N,D = Xdata.shape
    data = data - np.mean(data, axis = 0)
    Xdata = [data]
    ######## Create the Distribution object ##############################################
    
    #### 1st Gaussian Distribution
    Gaussian_d = Cdist.CDistribution(name = "Gaussian");
    Gaussian_d.set_distribution("Gaussian")
    Gaussian_d.parameters["mu_variance"]  = 0.2
    Gaussian_d.parameters["Sigma_min_init"] = 0.2
    Gaussian_d.parameters["Sigma_max_init"] = 0.3
    Gaussian_d.parameters["Sigma_min_singularity"] = 0.1
    Gaussian_d.parameters["Sigma_min_pdf"] = 0.1
    Gaussian_d.parameters["Sigma"] = "full"
    
    #### 1st Gaussian Distribution
    Gaussian_d2 = Cdist.CDistribution(name = "Gaussian2");
    Gaussian_d2.set_distribution("Gaussian")
    Gaussian_d2.parameters["mu_variance"]  = 0.2
    Gaussian_d2.parameters["Sigma_min_init"] = 0.2
    Gaussian_d2.parameters["Sigma_max_init"] = 0.3
    Gaussian_d2.parameters["Sigma_min_singularity"] = 0.1
    Gaussian_d2.parameters["Sigma_min_pdf"] = 0.1
    Gaussian_d2.parameters["Sigma"] = "diagonal"
    
    #### 2nd: Watson distribution
    Watson_d = Cdist.CDistribution(name = "Watson");
    Watson_d.set_distribution("Watson")
    Watson_d.parameters["Num_Newton_iterations"] = 5
    Watson_d.parameters["Allow_negative_kappa"] = "no"
    Watson_d.parameters["Kappa_max_init"] = 100
    Watson_d.parameters["Kappa_max_singularity"] =1000
    Watson_d.parameters["Kappa_max_pdf"] = 1000
    Watson_d.use_changeOfClusters = None
    #### 3rd von MisesFisher distribution ######
    vonMisesFisher_d = Cdist.CDistribution(name = "vonMisesFisher");
    vonMisesFisher_d.set_distribution("vonMisesFisher")
    
    vonMisesFisher_d.parameters["Num_Newton_iterations"] = 2
    vonMisesFisher_d.parameters["Kappa_max_init"] = 20
    vonMisesFisher_d.parameters["Kappa_max_singularity"] =1000
    vonMisesFisher_d.parameters["Kappa_max_pdf"] = 1000
    ### Add them together in the Manager
    myDManager = Cdist.CDistributionManager()
    K_G =  2  # Number of clusters for the Gaussian Distribution
    K_G2 = 0  # Number of clusters for the Gaussian Distribution
    K_W = 0
    K_vMF = 0
    if (K_G > 0):
        myDManager.add_distribution(Gaussian_d, Kd_list = range(0,K_G))
    if(K_W > 0):
        myDManager.add_distribution(Watson_d, Kd_list = range(K_G,K_W+ K_G))
    if(K_vMF > 0):
        myDManager.add_distribution(vonMisesFisher_d, Kd_list = range(K_W+ K_G,K_W+ K_G+ K_vMF))
    if (K_G2 > 0):
        myDManager.add_distribution(Gaussian_d2, Kd_list = range(K_W+ K_G+ K_vMF,K_W+ K_G+ K_vMF+K_G2))
        
#    Gaussian_d.set_parameters(parameters)
    ############# SET TRAINNG PARAMETERS ##################################
    K = len(myDManager.clusterk_to_Dname.keys())
    Ninit = 10
    delta_ll = 0.02
    T = 50
    verbose = 1;
    clusters_relation = "independent"   # MarkovChain1  independent
    time_profiling = None
    
    
    ############# Create the EM object and fit the data to it. #############
    myEM = CEM.CEM( distribution = myDManager, clusters_relation = clusters_relation, 
                   T = T, Ninit = Ninit,  delta_ll = delta_ll, 
                   verbose = verbose, time_profiling = time_profiling)

    ### Set the initial parameters
    theta_init = None
    model_theta_init = None
    ############# PERFORM THE EM #############
    
    logl,theta_list,model_theta_list = myEM.fit(Xdata, model_theta_init = model_theta_init, theta_init = theta_init) 
    
    spf.print_final_clusters(myDManager,clusters_relation, theta_list[-1], model_theta_list[-1])
    
    #######################################################################################################################
    #### Plot the evolution of the centroids likelihood ! #####################################################
    #######################################################################################################################

    gl.init_figure()
    gl.plot(range(1,np.array(logl).flatten()[1:].size +1),np.array(logl).flatten()[1:], 
            legend = ["EM LogLikelihood"], 
    labels = ["Convergence of LL with generated data","Iterations","LL"], 
    lw = 2)
    gl.savefig(folder_images +'%iSymbols_%iK_Likelihood_Evolution_'%(2,K) + clusters_relation+ "_"+str(periods[0])+ '.png', 
           dpi = 100, sizeInches = [12, 6])
    
    K = len(theta_list[-1])
    if(perform_HMM_after_EM):
        Ninit = 1
        ############# Create the EM object and fit the data to it. #############
        clusters_relation = "MarkovChain1"   # MarkovChain1  independent
        myEM = CEM.CEM( distribution = myDManager, clusters_relation = clusters_relation, 
                       T = T, Ninit = Ninit,  delta_ll = delta_ll, 
                       verbose = verbose, time_profiling = time_profiling)
    
        if(1):
            theta_init = theta_list[-1]
            A_init = np.concatenate([model_theta_list[-1][0] for k in range(K)], axis = 0)
            model_theta_init = [model_theta_list[-1], A_init]
        else:
            theta_init = None
            model_theta_init = None
            
        ############# PERFORM THE EM #############
        
        """
        For the HMM we can split the data into its different days
        """
        TD_new_filtered_dates = pd.DataFrame(dates)
        TD_new_filtered_dates.index = dates
        days_keys, day_dict = Cartera.get_timeData(symbolIDs[symbol_ID_indx1],periods[0]).get_indexDictByDay(TD = TD_new_filtered_dates)
        Xdata = [data[day_dict[k],:] for k in days_keys]
        
        
        logl,theta_list,model_theta_list = myEM.fit(Xdata, model_theta_init = model_theta_init, theta_init = theta_init) 
        
        spf.print_final_clusters(myDManager, clusters_relation, theta_list[-1], model_theta_list[-1])
        #######################################################################################################################
        #### Plot the evolution of the centroids likelihood ! #####################################################
        #######################################################################################################################
        
        gl.plot(range(1,np.array(logl).flatten()[1:].size +1),np.array(logl).flatten()[1:], 
                legend = ["HMM LogLikelihood"], 
        labels = ["Convergence of LL with generated data","Iterations","LL"], 
        lw = 2)
        gl.savefig(folder_images +'%iSymbols_%iK_Likelihood_Evolution_'%(2,K) + clusters_relation+ "_"+str(periods[0])+ '.png', 
               dpi = 100, sizeInches = [12, 6])


if(final_clusters_graph):

    K = len(theta_list[-1])
    gl.init_figure()
    ax1 = gl.scatter(ret1, ret2, alpha = 0.2, color = "k",
               legend = ["Data points %i"%(ret1.size)], labels = ["EM algorithm %i Gaussian fits"%(K),symbol_ID1,symbol_ID2])
    
    for k in range(K):
        mu_k = theta_list[-1][k][0]
        std_k = theta_list[-1][k][1]
        model_theta_last = model_theta_list[-1]
        

        mean,w,h,theta = bMA.get_gaussian_ellipse_params( mu = mu_k, Sigma = std_k, Chi2val = 2.4477)
        r_ellipse = bMA.get_ellipse_points(mean,w,h,theta)

        
        if (len(model_theta_last) == 1):
            pi = model_theta_last[0]
            gl.plot(r_ellipse[:,0], r_ellipse[:,1], ax = ax1, ls = "-.", lw = 3,
                AxesStyle = "Normal2", 
                legend  = ["Kg(%i), pi:%.2f"%(k+1,pi[0,k])])  
        else:
            pi = model_theta_last[0]
            A = model_theta_last[1]
            gl.plot(r_ellipse[:,0], r_ellipse[:,1], ax = ax1, ls = "-.", lw = 3,
                AxesStyle = "Normal2", 
                    legend = ["Kg(%i), pi:%.2f, A: %s"%(k+1,pi[0,k], str(A[k,:]))])  
        
        ax1.axis('equal')
    gl.set_fontSizes(ax = [ax1], title = 20, xlabel = 20, ylabel = 20, 
                      legend = 12, xticks = 10, yticks = 10)
    
    gl.subplots_adjust(left=.09, bottom=.10, right=.90, top=.95, wspace=.01, hspace=0.01)

    gl.savefig(folder_images +'%iGaussK_2Symbol_EM_'%K+ clusters_relation+ "_"+str(periods[0])+ '.png', 
               dpi = 100, sizeInches = [18, 6])
    
if (responsibility_graph):

    TD_new_filtered_dates = pd.DataFrame(dates)
    TD_new_filtered_dates.index = dates
    days_keys, day_dict = Cartera.get_timeData(symbolIDs[0],periods[0]).get_indexDictByDay(TD = TD_new_filtered_dates)
    Xdata = [data[day_dict[k],:] for k in days_keys]
    Xdata_dates = [dates[day_dict[k]] for k in days_keys]
    
    days_plot =  13 # len(Xdata_dates) # 18
    
    new_ll = myEM.get_loglikelihood(Xdata,myDManager, theta_list[-1],model_theta_list[-1])
    r = myEM.get_responsibilities(Xdata,myDManager, theta_list[-1],model_theta_list[-1])
    
    if (myEM.clusters_relation == "independent"):
        Nsam, K = r.shape
    elif(myEM.clusters_relation == "MarkovChain1"):
        Nsam, K = r[0].shape
    
    
    # Plotting 
    
    legend = [" K = %i"%i for i in range(K)]
    ax1 = None
    legend = []
    
    labels_title = "Cluster responsibility for the EM"
    
    if (1):
        """
        We plot them on top of each other
        """
        dataTransform = None
        nf = 1
        for i in range(len(Xdata_dates)):
            Xdata_dates[i] = Xdata_dates[i].time
    else:
        """
        We plot them on as a sequence
        """
        nf = 0
        
    gl.init_figure()
    Ndiv = 4
    
    axes_l = []
    for i in range(days_plot):
        chain = Xdata[i]
        r = myEM.get_responsibilities([chain],myDManager, theta_list[-1],model_theta_list[-1])
#        r = myEM.get_alpha_responsibilities([chain],myDManager, theta_list[-1],model_theta_list[-1])
        if (myEM.clusters_relation == "independent"):
           resp = r
        elif(myEM.clusters_relation == "MarkovChain1"):
            resp = r[0]
    
        Nclusters = resp.shape[1]
        ax_ii = gl.subplot2grid((days_plot,Ndiv), (i,0), rowspan=1, colspan=Ndiv-1) 
        ax1 = gl.plot_filled(Xdata_dates[i],resp , nf = 0, fill_mode = "stacked", legend = legend, 
                             sharex = ax1, sharey = ax1, AxesStyle = "Normal - No xaxis - No yaxis", labels = [labels_title,"","%i"%i],
                             dataTransform  = dataTransform, step_mode = "yes")
        
        gl.colorIndex = 0
        labels_title = ""
        axes_l.append(ax_ii)
    
    gl.subplots_adjust(left=.09, bottom=.20, right=.90, top=.95, wspace=.2, hspace=0.001)
    ax_i = gl.subplot2grid((days_plot,Ndiv), (0,Ndiv-1), rowspan=int(days_plot/2), colspan=1) 
    for i in range(1,K+1):
        gl.scatter(0, i, legend = [" K = %i"%(i)], lw = 28, AxesStyle = "Normal - No xaxis - No yaxis" , loc = "center left")
        
    gl.subplots_adjust(left=.09, bottom=.10, right=.90, top=.95, wspace=.2, hspace=0.01)
    image_name = "EM_%iSymbol_timeAnalysis_%iclusters"%(2,K)+ clusters_relation+ "_"+str(periods[0])+ '.png'
#    
    gl.set_fontSizes(ax = axes_l, title = 20, xlabel = 20, ylabel = 20, 
                      legend = 35, xticks = 25, yticks = 10)
    
    gl.set_fontSizes(ax = ax_i, title = 20, xlabel = 20, ylabel = 20, 
                      legend = 30, xticks = 20, yticks = 10)
    gl.set_zoom(xlim = [10,10.50])
    
    gl.savefig(folder_images + image_name, 
               dpi = 100, sizeInches = [30, 12])

 
## Save to disk the clusters
#    mus_kk = []
#    for i in range(K):
#        mus_kk.append(theta_list[-1][i][0])
#    
#    mus_kk = np.concatenate(mus_kk,axis = 1)
#    
#    
##    df = pd.DataFrame(mus_kk)
##    df.to_csv(folder_images + "file_path.csv")
#
#    np.savetxt(folder_images + "clusters.csv", mus_kk, delimiter=",")