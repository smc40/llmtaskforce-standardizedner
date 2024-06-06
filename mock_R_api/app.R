# Load the plumber package
library(plumber)

# Create the plumber router
r <- plumb("endpoints.R")

# Run the API
r$run(host = "0.0.0.0", port = 8002)
