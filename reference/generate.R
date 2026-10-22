# Original PyRverse driver. Calls public base/stats APIs; no upstream source is copied.
# Run from the repository root through reference/generate.py.
cases <- read.csv("datasets/summary.csv", stringsAsFactors = FALSE,
                  na.strings = NULL, colClasses = "character")
calculate <- function(i) {
  tokens <- if (nchar(cases$values[i]) == 0) character(0) else
    strsplit(cases$values[i], ";", fixed = TRUE)[[1]]
  x <- as.numeric(tokens)
  remove_missing <- cases$remove_missing[i] == "true"
  data.frame(case = cases$case[i], mean = mean(x, na.rm = remove_missing),
             sample_variance = var(x, na.rm = remove_missing))
}
result <- do.call(rbind, lapply(seq_len(nrow(cases)), calculate))
# write.table uses limited digits for numeric columns. Format explicitly before
# writing to preserve float64 values rather than truncating reference precision.
for (column in c("mean", "sample_variance")) {
  result[[column]] <- ifelse(is.na(result[[column]]), "NaN",
                             sprintf("%.17g", result[[column]]))
}
write.table(result, "reference/summary.csv", sep = ",", row.names = FALSE,
            col.names = TRUE, quote = FALSE, na = "NaN", eol = "\n")
writeLines(capture.output(sessionInfo()), "reference/session-info.txt", useBytes = TRUE)
cat(R.version.string, "\n")
