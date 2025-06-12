class NewInputFile:
    
    def change_elevation(self,data, option2, textvalue):
        newdata=[]
        start_node=False
        
        for row in data : 
            # print(row[0])
            
            if(row[0]=='' and start_node==True):
                start_node=False
            
            if(start_node==True and int(row[0])==int(option2)):
                row[2]=textvalue
            
            if(row[0] == 'Node ID'):
                start_node = True
            
            newdata.append(row)
        
        return newdata
    
    def change_demand(self, data, option2, textvalue):
        newdata=[]
        start_node=False
        
        for row in data : 
            
            if(row[0]=='' and start_node==True):
                start_node=False
            
            if(start_node==True and int(row[0])==int(option2)):
                row[3]=textvalue
                # print("Demand row : " + row)
            
            if(row[0] == 'Node ID'):
                start_node = True
            
            newdata.append(row)
        
        return newdata
    
    def change_pipe_parallel(self, data, option2, textvalue):
        newdata=[]
        start_pipe=False
        
        for row in data : 
            
            if(row[0]=='' and row[4]=='' and start_pipe==True):
                start_pipe=False
            
            if(start_pipe==True and int(row[0])==int(option2)):
                row[6]= 1 if (row[6]==0 or row[6]=='') else 0
                # print("Pipe row : " + row)
            
            if(row[0] == 'Pipe ID'):
                start_pipe = True
            
            newdata.append(row)
        
        return newdata
    
    def remove_commercial_pipe(self, data, option2, textvalue):
        newdata=[]
        start_pipe=False
        
        for row in data : 
            
            if(row[0]=='' and start_pipe==True):
                start_pipe=False
            
            if(start_pipe==True and int(row[0])==int(option2)):
                # print("Commercial Pipe row : " + row)
                continue
            
            if(row[0] == 'Diameter'):
                start_pipe = True
            
            newdata.append(row)
        
        return newdata
    
    def add_commercial_pipe(self, data, option2, textvalue):
        newdata=[]
        start_pipe=False
        values = textvalue.split()
        n=len(data[0])
        
        for i in range(2,n):
            values.append('')
        
        for row in data : 
            
            if(row[0]=='' and start_pipe==True):
                start_pipe=False
            
            if(start_pipe==True and int(row[0])>int(values[0])):
                # print("Commercial row : " + values)
                newdata.append(values)
            
            if(row[0] == 'Diameter'):
                start_pipe = True
            
            newdata.append(row)
        
        return newdata