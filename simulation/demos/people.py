import numpy as np

from .randomness import choose, uniform
from .state import PEOPLE, PREFERENCES


def citizens(ids, born, sex, seed, month):
    people = np.zeros(len(ids), dtype=PEOPLE)
    people["id"], people["born"], people["sex"] = ids, born, sex
    for field in ("household", "parent", "partner", "firm"):
        people[field] = -1
    age = month - born
    education = uniform(seed, "education", month, ids)
    people["education"] = np.where(age < 216, 0, np.where(education < .20, 1, np.where(education < .72, 2, 3)))
    people["skills"] = np.minimum(100, people["education"] * 20 + uniform(seed, "skills", month, ids) * 40)
    update_health(people, seed, month)
    common = uniform(seed, "preferences-latent", month, ids)
    for field in PREFERENCES:
        people[field] = 100 * (.25 * common + .75 * uniform(seed, f"preference/{field}", month, ids))
    return people


def update_health(people, seed, month):
    years = (month - people["born"]) / 12
    limitations = uniform(seed, "health-limitation", 0, people["id"]) < np.minimum(.65, .018 + (years / 135)**3)
    people["limitations"] = limitations
    people["health"] = np.where(limitations, 2, np.where(years >= 65, 1, 0))
    people["autonomy"] = np.where(limitations, 65, 100)
    people["care"] = limitations | (years < 2)


def initial_people(config, seed):
    ids = np.arange(config["population"], dtype=np.int64)
    if "empirical" in config:
        flat = np.asarray(config["empirical"]["age_sex_counts"]["2022"]).ravel()
        strata = choose(flat, uniform(seed, "initial-age-sex", 0, ids))
        sex, years = strata // 101, strata % 101
    else:
        sex = uniform(seed, "initial-sex", 0, ids) >= .5
        years = np.minimum(100, 10 * choose(config["demonstration_age_weights"], uniform(seed, "initial-decade", 0, ids))
                           + (10 * uniform(seed, "initial-year", 0, ids)).astype(int))
    born = -12 * years - (12 * uniform(seed, "initial-age-month", 0, ids)).astype(int)
    return citizens(ids, born, sex, seed, 0)
