from ctypes import c_int
#--------------------------------------------------------------------------------------------------
def solve_knapsack (kp_instance, knapsack_solver):
    #kp_instance is a tuple: (  {"gene":benefit},  {"gene":damage},  knapsack_size(=tolerance)   )
    B_dict, D_dict, T_edges, N  = kp_instance[0][0], kp_instance[0][1], kp_instance[0][2], len(kp_instance[0][0].keys())
    assert (N==len(B_dict)==len(D_dict))
    if N == 0:
        return []
    else:
        GENES_in, grey_genes, green_genes, red_genes = [], [], [], []
        G, B, D = [],[],[]
        GENES_in, GENES_out = [],[]
        #attempt to compress, compiler might already handle though
        i=0
        for key in B_dict.keys():
            if (B_dict[key]>0 and D_dict[key] > 0):
                grey_genes.append(key)
                G.append(key)
                i += 1
            elif (B_dict[key]>0 and D_dict[key]==0):
                green_genes.append(key)
                GENES_in.append((key, B_dict[key], D_dict[key], 1))
            elif (B_dict[key]==0):
                red_genes.append(key)
                GENES_out.append((key, B_dict[key], D_dict[key], 0))

        assert (len(grey_genes)+len(green_genes)+len(red_genes)) == len (B_dict.keys())
        N = len (grey_genes)
        F, solver_returns = (c_int*N)(),  (c_int*4)()
        G, B, D, i = ['' for x in range(0,N)],(c_int*N)(),(c_int*N)(), 0
        for key in grey_genes:          #ASK MOH, should be able to merge with above loop  
            G[i],B[i], D[i], i = key,B_dict[key],D_dict[key], i+1
        #---------------------------------------------------------------------    
        knapsack_solver.solve (B, D, T_edges, N, F, solver_returns)   # WARNING: minknap.so does not return the correct knapsack weight (solver_returns[1])                          
        #---------------------------------------------------------------------
        #old: TOTAL_Bin, TOTAL_Din, TOTAL_Bout, TOTAL_Dout, GENES_in, GENES_out = 0, 0, 0, 0, [], []
        
        for g in range (0, N):
            if F[g] == 1:
                GENES_in.append ((G[g], B[g], D[g], F[g]))
            else:
                GENES_out.append ((G[g], B[g], D[g], F[g]))

        ALL_GENES = GENES_in+GENES_out
        assert(len(ALL_GENES)==len(GENES_in) + len(GENES_out)) 
        assert(len(GENES_in) + len(GENES_out) == len(green_genes) + len(red_genes) + len(grey_genes))
        coresize  =  solver_returns[2] #if DP_solver.so is used,  coresize = len (grey_genes)      
        execution_time = solver_returns[3]
        return [GENES_in, ALL_GENES, len(green_genes), len(red_genes), len(grey_genes), execution_time]
# --------------------------------------------------------------------------------------------------
