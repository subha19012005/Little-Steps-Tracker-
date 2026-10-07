args <- commandArgs(trailingOnly = TRUE)

if (length(args) != 5) {
  write("Invalid Anthro input.", stderr())
  quit(status = 2)
}

if (!requireNamespace("anthro", quietly = TRUE)) {
  write("The CRAN anthro package is not installed.", stderr())
  quit(status = 2)
}

sex <- args[[1]]
age_days <- as.numeric(args[[2]])
weight_kg <- as.numeric(args[[3]])
lenhei_cm <- as.numeric(args[[4]])
measure <- args[[5]]

result <- anthro::anthro_zscores(
  sex = sex,
  age = age_days,
  is_age_in_month = FALSE,
  weight = weight_kg,
  lenhei = lenhei_cm,
  measure = measure
)

columns <- c(
  "zlen", "zwei", "zwfl", "zbmi", "cbmi", "clenhei", "cmeasure",
  "flen", "fwei", "fwfl", "fbmi"
)
if (!all(columns %in% names(result))) {
  write("The installed anthro package returned an unexpected result.", stderr())
  quit(status = 2)
}

output <- as.data.frame(
  lapply(columns, function(column) result[[column]][[1]]),
  stringsAsFactors = FALSE
)
names(output) <- columns
write.csv(output, row.names = FALSE, na = "")