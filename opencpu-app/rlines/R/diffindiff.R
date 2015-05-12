#' Take region names and a comparison date and does diff-in-diff
#' 
#' @param target.region: The region of interest, matching a backpage domain
#' @param comparison.region.set: A set of regions (e.g. c('nova','abilene')) to compare to
#' @param event.date: a YYYY-MM-DD date string for the actual event date
#' @param logged: A boolean as to whether to perform a log transform on the data first
#' @return A list with dd, main_diff, comparison_diff, pre, and post values



diffindiff<-function(target.region, comparison.region.set, event.date, logged=FALSE, normalize=FALSE){
  data=twolines(target.region=target.region, comparison.region.set=comparison.region.set)
  data$date<-as.Date(data$MonthDate, "%Y-%m-%d")
  data$MonthDate <-NULL
  
  ed<-as.Date(event.date, "%Y-%m-%d")
  
  data$post = data$date > ed
  data <- data[data$date > as.Date("2013-09-01","%Y-%m-%d"),]
  data <- data[data$date < as.Date("2014-06-01","%Y-%m-%d"),]
  data<-melt(data, id=c("date","post"), variable.name="group", value.name="counts")
  if (logged){
    data$counts<-log(1+data$counts)
  }
  pre.target.avg<-mean(data[data$post==FALSE & data$group == "Target",'counts'])
  pre.comparison.avg<-mean(data[data$post==FALSE & data$group == "Comparison",'counts'])
  if (normalize){
   data$counts[data$group == "Comparison"] <- data$counts[data$group == "Comparison"] * pre.target.avg/pre.comparison.avg
  }
  data <- within(data, group <- relevel(group, ref = "Comparison")) # Set comparison as base group
  model<-lm(counts ~ post*group, data=data)
  msum<-summary(model)
  df<-msum$df[2]
  print(summary(model))
  
  # The idea for this model is for the results to be in the order:
  #  1: (Intercept)           
  #  2: postTRUE            
  #  3: groupTarget         
  #  4: postTRUE:groupTarget
  model.results<-coef(summary(model))
  vcov.matrix<-vcov(model)
  ###
  # We build a dataframe here which has the estimate, std error, t stat, and p value for 
  # 3 key estimates that we'd like to see:
  # -The diff in diff estimate
  # -The change at the event date in the target group
  # -The change at the event date in the control group
  d<-data.frame(b=rep(NA,3), se=rep(NA,3), t=rep(NA,3), p=rep(NA,3),row.names=c('diff_in_diff','target_diff','comparison_diff'))
  d['diff_in_diff','b'] <- model.results[4,'Estimate']
  d['diff_in_diff','se'] <- model.results[4, "Std. Error"]
  d['diff_in_diff','t'] <- model.results[4, "t value"]
  d['diff_in_diff','p'] <- 2*pt(-abs(model.results[4, "t value"]),df=df-1)

  target.change.vec<-c(0,1,0,1)
  # The target change is the sum of the 2nd and 4th variables (set target=True and change post from 1 to 0)
  b.target<-target.change.vec %*% model.results[,'Estimate']
  se.target<-sqrt(target.change.vec %*% vcov.matrix %*% target.change.vec)
  d['target_diff','b'] <- b.target[1,1]
  d['target_diff','se'] <- se.target[1,1]
  d['target_diff','t'] <- b.target[1,1]/se.target[1,1]
  d['target_diff','p'] <- 2*pt(-abs(b.target[1,1]/se.target[1,1]),df=df-1)
  
  comparison.vec<-c(0,1,0,0)
  # The comparison group is the sum of the 1st and 4th variables
  b.comparison<-comparison.vec %*% model.results[,'Estimate']
  se.comparison<-sqrt(comparison.vec %*% vcov.matrix %*% comparison.vec)
  d['comparison_diff','b'] <- b.comparison[1,1]
  d['comparison_diff','se'] <- se.comparison[1,1]
  d['comparison_diff','t'] <- b.comparison[1,1]/se.comparison[1,1]
  d['comparison_diff','p'] <- 2*pt(-abs(b.comparison[1,1]/se.comparison[1,1]),df=df-1)
  
  names(d)<-c('estimate','standard error','t-statistic','p-value')
  return(d)
}
