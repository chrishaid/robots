####################################################################################
## Script to transform
## Long format Kicboard culture csv
## to wide format (by behavoir event), where 
## each student is represented by 2(!) rows
## One row for negative paycheck events (i.e., deductions)
## and the other row for postive (though value 0) culture events (Create Points)
#################################################################################

# Get Arguments for dates or autmaticalluy generate weeklong dates depending on 

args<-commandArgs(T)
print(paste("Length of args is ",length(args),sep=""))
print(args)


#Load Libraries
library(reshape)
library(plyr)
library(lubridate)


todays.date<-today()
if(length(args)==0) {
  start.date <- floor_date(today(), unit="week")-weeks(1)+days(1)
  end.date <- floor_date(today(), unit="week")
}

if(length(args)==1){
  start.date<-floor_date(ymd(args[1]), unit="week") - days(1)
  end.date<-start.date+days(6) 
  print(start.date)
  print(end.date)
}

if(length(args)==2){
  start.date<-floor_date(ymd(args[1]), unit="week")
  end.date<-floor_date(ymd(args[2]), unit="week")
}

#Get Kickboard culture data for Create and Bloom

for(i in c("KCCP", "KBCP")){
  print(sprintf("Loading %s Kickboard data . . . ", i))
  in.file<-paste(i, "_culture-analysis_",format(todays.date,"%y%m%d"),".csv", sep="")
  kb.long<-read.csv(in.file)
  
  #Discriminate between Create Points and Paycheck Decutions
  print("Separating merit points and paycheck deductions . . . ")
  kb.long$CreatePoint<-is.na(kb.long$Dollar.Value)
  
  #Remove any deposit.
  print("Removing depostis . . . ")
  kb.nodeposit<-subset(kb.long, Behavior!="Deposit")
  
  #This functino simply prodives consecutive numbering to a sorted dataframe
  consecutive<-function(df){
    df$OrderID<-c(1:nrow(df))
    return(df)
  }
  
  #Data Range to rearrange
  print("Subseting date range . . . ")
  x.long<-subset(kb.nodeposit, ymd(as.character(Behavior.Date))>=start.date
                 & ymd(as.character(Behavior.Date))<=end.date)
  
  #Change numeric to factors so that values don't get NA's during melt opoeration (see next line)
  x.long$Dollar.Value<-as.factor(x.long$Dollar.Value)
  #make what is long even longer
  x<-melt(x.long, id.vars=c("Student","Group","CreatePoint"), measure.vars=c("Behavior", "Dollar.Value", "Behavior.Date", "Staff", "Comments"))
  
  #rename variables to comport with Kate's mail merge input spreadsheet column headers
  print("Renaming variables . . . ")
  levels(x$variable)<-c("Behavior", "Dollar", "Date", "Staff", "Comments")
  
  #add numbering for each event
  print("Numbering events . . . ")
  x<-ddply(x, .(Student, CreatePoint, variable), function(df) consecutive(df))
  #rename the variables with number, name, number (the first number is later dropped, it is used for ordering (thouhg I think this can be deprecated))
  x$variable2<-paste(x$OrderID, x$variable, x$OrderID, sep=" ")
  
  #get max number of student events for the period
  n<-max(x$OrderID)
  
  #go from long to wide and rearrange by group and student names
  print("Convert from long to wide table. . . ")
  x.wide<-arrange(cast(x, Student+Group+CreatePoint~variable2), Group, Student)
  
  #strip leading number from column headers
  names(x.wide)[-(1:3)]<-gsub("(\\d{1,2})(\\s)(Behavior|Date|Comments|Dollar|Staff)(\\s)(\\d{1,2})", "\\3\\4\\5",   names(x.wide)[-(1:3)])
  
  #reorder columns to comport with Kate's mail merge input spreadsheet
  col.order<-vector()
  cats<-c("Behavior", "Dollar","Date", "Staff", "Comments")
  for(j in 1:n){
    cols.new<-paste(cats, j, sep=" ")
    col.order<-c(col.order, cols.new)
  } 
  #Get paycheck totals (50 +  the sume of negative decuctions)
  print("Calculating paycheck totals . . . ")
  paycheck<-ddply(subset(x, variable=="Dollar"), .(Student, Group), summarise, Paycheck=50+sum(as.numeric(levels(value))[value],na.rm=T))
  
  #merge paycheck totals with events 
  print("Mergig paycheck totals with events . . . ")
  x.merge<-merge(x=x.wide, y=paycheck, by.x=c("Student", "Group"), by.y=c("Student","Group"), all.x=T)  
  
  #rearrange and drop unnecessary columns 
  z<-x.merge[,c("Student", "Group","Paycheck", col.order)]
  
  #rename Group to Homeroom
  names(z)[2]<-"Homeroom"
  
  #resort order by Group name and then Student name
  z<-arrange(z,Homeroom, Student)
  
  #write the file
  print("Writing file . . . ")
  out.file<-paste(i,"_KB_",format(todays.date,"%y%m%d"),".csv",sep="")
  write.csv(z,out.file, row.names=FALSE)
  
  print(paste(i, " Kickboard Data saved to: ",out.file,sep=""))

} #end Schools for loop

