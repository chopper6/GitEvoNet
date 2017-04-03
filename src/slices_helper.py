# degree_frequency = {degree:frequency}
# 'slices' needs to be populated with the average frequency of given nodes of degree x to belong to a slice (a,b)
def fill_slices(node_info):
    slice_freq = gen_slice_freq(node_info)

    # [slice][deg] = freq
    slices = [None for i in range(2)]
    for i in range(2):
        slices[i] = {    'interval':10,
                             'segments':{
                                     1  :{'degree_freq':{},  'color':None, 'avg':0, 'std':0, 'label':'100:0', 'range':(100,0)},
                                     2  :{'degree_freq':{},  'color':None, 'avg':0, 'std':0, 'label':'90:10', 'range':(90,10)},
                                     3  :{'degree_freq':{},  'color':None, 'avg':0, 'std':0, 'label':'80:20', 'range':(80,20)},
                                     4  :{'degree_freq':{},  'color':None, 'avg':0, 'std':0, 'label':'70:30', 'range':(70,30)},
                                     5  :{'degree_freq':{},  'color':None, 'avg':0, 'std':0, 'label':'60:40', 'range':(60,40)},
                                     6  :{'degree_freq':{},  'color':None, 'avg':0, 'std':0, 'label':'50:50', 'range':(50,50)},
                                     7  :{'degree_freq':{},  'color':None, 'avg':0, 'std':0, 'label':'40:60', 'range':(40,60)},
                                     8  :{'degree_freq':{},  'color':None, 'avg':0, 'std':0, 'label':'30:70', 'range':(30,70)},
                                     9  :{'degree_freq':{},  'color':None, 'avg':0, 'std':0, 'label':'20:80', 'range':(20,80)},
                                     10 :{'degree_freq':{},  'color':None, 'avg':0, 'std':0, 'label':'10:90', 'range':(10,90)},
                                     11 :{'degree_freq':{},  'color':None, 'avg':0, 'std':0, 'label':'0:100', 'range':(0,100)},
                                     12 :{'degree_freq':{},  'color':None, 'avg':0, 'std':0, 'label':'0:0',   'range':(0,0)}
                                    }
        }
        #i think this is how: [0 as segment][slice#][0 as degree_freq]
    
        for slice_num in range(1,len(slice_freq[i])):
            for deg in range(len(slice_freq[i][slice_num])):
                if deg in slices[i]['segments'][slice_num]['degree_freq'].keys():
                    slices[i]['segments'][slice_num]['degree_freq'][deg] += slice_freq[i][slice_num][deg]
                else:
                    slices[i]['segments'][slice_num]['degree_freq'][deg] = slice_freq[i][slice_num][deg]

    return slices

##################################################################
def assign_slice_num(B,D):
    #assumes intervals of 10
    # returns (B inteval, D interval)
    if (B==0):
        if (D==0): slice_num, srange = 12, (0,0)
        else: slice_num, srange = 1, (100,0)

    else:
        fraction = round((float(B)/float(B+D))*100, 12)
        if (fraction< 5): slice_num, srange = 11, (0,100)
        elif (fraction< 15): slice_num, srange = 10, (10,90)
        elif (fraction < 25): slice_num, srange = 9, (20,80)
        elif (fraction < 35): slice_num, srange = 8, (30,70)
        elif (fraction < 45): slice_num, srange = 7, (40,60)
        elif (fraction < 55): slice_num, srange = 6, (50,50)
        elif (fraction < 65): slice_num, srange = 5, (60,40)
        elif (fraction < 75): slice_num, srange = 4, (70,30)
        elif (fraction < 85): slice_num, srange = 3, (8,20)
        elif (fraction < 95): slice_num, srange = 2, (90,10)
        else: slice_num, srange = 1, (100,0)


    return slice_num, srange


def gen_slice_freq(node_info):
    #node_info: np obj w/ # [file, B, D, features]
    #frequency = feature 0
    maxDeg = len(node_info[0])
    slice_freq = [[[0 for i in range(maxDeg*2)] for j in range(13)] for k in range(2)]
    # [slice][deg] = freq

    #print(len(slice_freq), len(slice_freq[0]))
    for B in range(len(node_info[0])):
        for D in range(len(node_info[0][B])):
            slice_num, srange = assign_slice_num(B,D)
            #print(slice_num, B+D, B, D)
            slice_freq[0][slice_num][B+D] += node_info[0,B,D,0]


    #print(len(slice_freq), len(slice_freq[0]))
    for B in range(len(node_info[-1])):
        for D in range(len(node_info[-1][B])):
            slice_num, srange = assign_slice_num(B,D)
            #print(slice_num, B+D, B, D)
            slice_freq[1][slice_num][B+D] += node_info[-1,B,D,0]

    return slice_freq




def assign_range(slices, b, d):
    right_key, b2d_ratio, d2b_ratio = 0,0,0
    if b==0 and d==0:
        right_key =   [key for key in slices['segments'].keys() if slices['segments'][key]['range'][0]==0 and  slices['segments'][key]['range'][1]==0]

    elif b>=d: 
        b2d_ratio, d2b_ratio = round((float(b)/float(b+d))*100, 12), round((float(d)/float(b+d))*100,12)
        right_key = [key for key in slices['segments'].keys() if (b2d_ratio-slices['segments'][key]['range'][0]) >=0 and (b2d_ratio-slices['segments'][key]['range'][0]) <slices['interval']  and (slices['segments'][key]['range'][1]-d2b_ratio)>=0 and (slices['segments'][key]['range'][1]-d2b_ratio)<slices['interval'] ]
    
    else:
        b2d_ratio, d2b_ratio = (float(b)/float(b+d))*100, (float(d)/float(b+d))*100
        right_key = [key for key in slices['segments'].keys() if (slices['segments'][key]['range'][0]-b2d_ratio) >=0 and (slices['segments'][key]['range'][0]-b2d_ratio) <slices['interval']  and (d2b_ratio-slices['segments'][key]['range'][1])>=0 and (d2b_ratio-slices['segments'][key]['range'][1])<slices['interval'] ]
    
    
    assert len(right_key)==1
    return right_key[0]
#######################################################################################

