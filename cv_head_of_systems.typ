#import "content/data.typ": cv_data
#import "lib/template.typ": render_cv

#let filtered_experience = cv_data.experience.filter(entry =>
  entry.variant_tags.contains("head_of_systems")
)

#let filtered_skills = cv_data.skills.filter(cat =>
  cat.variant == "head_of_systems"
)

#let variant_data = cv_data + (
  experience: filtered_experience,
  skills: filtered_skills,
  certification: none,
)

#render_cv(variant_data, variant: "head_of_systems")