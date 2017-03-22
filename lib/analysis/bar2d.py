import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt 
from colour import Color
from matplotlib import rcParams
from matplotlib import patches as mpatches
import math

def update_rcParams_pie():
    rcParams['font.serif']= 'DejaVu Sans' #['Bitstream Vera Sans', 'DejaVu Sans', 'Lucida Grande', 'Verdana', 'Geneva', 'Lucid', 'Arial', 'Helvetica', 'Avant Garde', 'sans-serif']
    rcParams['grid.alpha'] = 0.1
    rcParams['axes.grid']=False
    rcParams['savefig.pad_inches']=.1
    rcParams['grid.color']='white'

    rcParams['axes.titlesize']   = 5
    rcParams['axes.titleweight'] = 'normal'
    rcParams['axes.linewidth']   = .5
    rcParams['axes.labelsize']   = 5
    rcParams['axes.labelpad']    = 2
    
    rcParams['xtick.color']        =  'black'    #  ax.tick_params(axis='x', colors='red'). This will set both the tick and ticklabel to this color. To change labels' color, use: for t in ax.xaxis.get_ticklabels(): t.set_color('red')
    rcParams['xtick.direction']    =  'out'      # ax.get_yaxis().set_tick_params(which='both', direction='out')
    rcParams['xtick.labelsize']    =  4
    rcParams['xtick.major.pad']    =  1
    rcParams['xtick.major.size']   =  3  # how long the tick is
    rcParams['xtick.major.width']  =  .4 
    rcParams['xtick.minor.visible']=  False


    rcParams['ytick.color']        =  'black'       # ax.tick_params(axis='x', colors='red')
    rcParams['ytick.direction']    =  'out'         # ax.get_xaxis().set_tick_params(which='both', direction='out')
    rcParams['ytick.labelsize']    =  4  
    rcParams['ytick.major.pad']    =  1 
    rcParams['ytick.major.size']   =  3  
    rcParams['ytick.major.width']  =  .4  
    rcParams['ytick.minor.pad']    =  1  
    rcParams['ytick.minor.size']   =  1  
    rcParams['ytick.minor.width']  =  .25 
    rcParams['ytick.minor.visible']=  False
    
    rcParams['legend.fontsize']    =  4   
    rcParams['legend.handleheight']=  0.5 
    rcParams['legend.handlelength']=  1.0 
    rcParams['legend.frameon']     =  False
    rcParams['legend.labelspacing']=  .2 
    rcParams['legend.borderaxespad']=  .1    
##################################################################
def update_rcParams_bar2d():
    update_rcParams_pie()
    rcParams['axes.labelsize']   = 7
    rcParams['xtick.labelsize']    =  5
    rcParams['ytick.labelsize']    =  rcParams['xtick.labelsize'] 
    rcParams['ytick.major.pad']    =  0.5
    rcParams['ytick.minor.pad']    =  0.5
##################################################################  
def palette_and_patches():
    all_degrees       = [d for d in range(1,1000,1)]
    maxd              = 20 # max(all_degrees)
    mind              = 1  #min(all_degrees)
    start             = Color('#ff00c8')#Color("#ff33e0") 
    middle1           = Color('#e999ff')#Color('#9333ff') 
    middle2           = Color('#0f4dff')#Color('#cfc9f8') # #3371ff
    end               = Color('#afcecc')#Color('#33f3ff')

    jump1             = 1 # must be >= 1, larger values = less distinct colors; increase it if start and middle are far-apart colors
    jump2             = 1
    cutoff_degree     = 4#min(4,math.ceil(maxd/2.0)) # must be >= 1

    palette_size1     = math.ceil(math.log(cutoff_degree,2)) + 1
    palette_size2     = math.ceil(math.log(maxd,2)) - math.floor(math.log(cutoff_degree,2)) 

    under_cutoff      = list(start.range_to   (middle1, max(1,palette_size1*jump1)))
    above_cutoff      = list(middle2.range_to (end,     max(1,palette_size2*jump2)))


    palette = {}
    for deg in all_degrees:#range (1, maxd+1,1):
        if deg <= cutoff_degree:
            index = math.ceil(math.log(deg,2)) + (jump1-1)
            palette[deg] = under_cutoff[index].rgb
        elif deg < maxd:
            index = math.ceil(math.log(maxd,2)) - math.ceil(math.log(deg,2)) + (jump2-1)
            palette[deg] = above_cutoff[index].rgb
        else:
            index = (jump2-1)
            palette[deg] = above_cutoff[index].rgb


    distinct_colors, patches, i = [], [], 1
    while True:
        distinct_colors.append(palette[i])
        current_color = palette[i]
        left = i
        i+=1
        while palette[i] == current_color:
            i+=1
            if i>maxd:
                break
        right = i
        label = None
        if i<=maxd:
            label = str(left)
            if right-left > 1:
                label += '-'+str(right-1)
            patches.append(mpatches.Patch(color=current_color, label=label))
        else:
            label = '>='+str(maxd)
            patches.append(mpatches.Patch(color=current_color, label=label))
            break
    return palette, patches, "degree:"
##################################################################   
def normalize(slices):
    for slice_id in slices.keys():
        total = sum(slices[slice_id].values())
        for degree in slices[slice_id].keys():
            if (total != 0): slices[slice_id][degree] = (slices[slice_id][degree]/total)*100
##################################################################  
def extract_stats(slices):
    slices2 = {}
    all_degrees = []
    group_labels = []
    for slice_id in sorted(slices['segments'].keys()):
        if slices['segments'][slice_id]['range']==(0,0):# skip 0:0 slice
            continue
        slices2[slice_id] = {}
        group_labels.append(slices['segments'][slice_id]['label'])
    for slice_id in slices2.keys():
        for degree in sorted(slices['segments'][slice_id]['degree_freq'].keys()):
            freq = slices['segments'][slice_id]['degree_freq'][degree] #['avg_so_far']
            slices2[slice_id][degree] =  freq
            all_degrees.append(degree)
    all_degrees = sorted(list(set(all_degrees)), reverse=True)
    return slices2, all_degrees, group_labels
##################################################################  
def customize_bar2d(ax, xlabels, xlabels_loc, title):
    ax.tick_params(axis='x', which='both', left='off', right='off', bottom='on', top='off',  labelbottom='on', labeltop='off') # both major and minor ticks
    ax.tick_params(axis='y', which='both', bottom='off', top='off', left='on', right='on',  labelleft='on', labelright='off') # both major and minor ticks             
    ax.set_xticks(xlabels_loc)
    ax.set_xlabel('benefit:bamage ratio group')
    ax.set_ylabel('% degree makeup (log)')
    ax.set_title(title)
    ax.set_xticklabels(xlabels,rotation='vertical')
    ax.spines['top'].set_visible(False)
    #ax.spines['right'].set_visible(False)
    ax.set_yscale('log', basey=10)#, subsx=[0,2,4,8,16], subsy=[0,2,4,8,16])
    ax.set_ylim([0,100]) # it matters where this line is, (it has to be before ticking is done i think)

    #TODO: add this back?
    #ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(LogYformatter))
    return ax
##################################################################  
def plot_bar2d(output_dir, name, slices):
    update_rcParams_bar2d()
    fig = plt.figure(figsize=(4,4))
    ax = fig.add_axes([.1,.1,.9,.9])

    DegFreqBySlice, all_degrees, group_labels = extract_stats (slices)
    palette, patches, legend_label            = palette_and_patches()
    normalize(DegFreqBySlice) ### normalize to 0-100%  ####


    N          = len(DegFreqBySlice.keys())
    tickloc    = [t for t in range(1,N+1,1)]
    width      = .9      # the width of the bars: can also be len(x) sequence
    bottom = [0]*N
    #ax.set_xticklabels(group_labels)
    for deg in sorted(all_degrees, reverse=True): #all_degrees are increasingly sorted, this makes a nice log-scale bar
        if (deg != 0):
            next_stack     = []
            for slice_id in sorted(DegFreqBySlice.keys()):        
                if deg in DegFreqBySlice[slice_id].keys():
                    next_stack.append(DegFreqBySlice[slice_id][deg])
                else:
                    next_stack.append(0)
            ax.bar(tickloc, next_stack, width, color=palette[deg], align='center', alpha=.9, edgecolor='white',linewidth=0.1, bottom=bottom)#, yerr=womenStd)
            bottom = [b+m for b,m in zip(bottom, next_stack)]
    
    #ax.plot([0., max(tickloc)+(width/2.)], [25, 25], "--", color='black', linewidth=1) # linestyle='-/--/-./:'   
    ax   = customize_bar2d(ax, group_labels, tickloc, "the title") # IMPORTANT: should be called after ax.bar is done
    legend = ax.legend(handles=patches, loc=(1.03,0.1), title='degree:') # http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend 
    legend.get_title().set_fontsize(5) # this is a must, can't do this thru rcParams

    plt.savefig(output_dir + "node_plots/" + "degree_percent_" + str(name) + ".png")
##################################################################  
