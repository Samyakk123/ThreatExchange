variable "prefix" {
  description = "Prefix to use for resource names"
  type        = string
}

variable "lambda_docker_info" {
  description = "Docker container information for lambda functions"
  type = object({
    uri = string
  })
}


variable "additional_tags" {
  description = "Additional resource tags"
  type        = map(string)
}
