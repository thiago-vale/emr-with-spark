locals {
  common_tags = {
    IES         = "IGTI"
    CURSO       = "EDC"
    Environment = "production"
    ManagedBy   = "Terraform"
    Project     = "EMR-Spark"
  }
}
