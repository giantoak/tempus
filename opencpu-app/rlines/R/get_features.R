#' Take region names and a comparison date and does diff-in-diff
#' 
#' @param target.region: The region of interest, matching a backpage domain
#' @param num.matches: the number of matches to return. Defaults to 4.
#' @return A data frame with:
#' - matched regions as rows
#' - features as columns
#' - score as a final column measuring similarity

get_features<-function(target.region, num.matches=4, region.var='region', comparison.vars){
  data<-region.features[,c(comparison.vars, region.var)] # Select columns to use
  data$target <- data$region == target.region # Create a binary 1 for the region we care about
  matching.formula<-paste(target.varname,'~',paste(comparison.vars,collapse=' + '))
  match<-matchit(as.formula(matching.formula), data=data)
  data$score <- match$distance
  target.row <- data[data$target,]
  data<-data[!data$target,]
  data<-data[order(data$score, decreasing=TRUE),]
  data<-data[1:num.matches,]
  data<-rbind(target.row,data)
  data<-subset(data, select=-c(target))
  return(data)
}
