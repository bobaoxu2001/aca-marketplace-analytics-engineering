with age_bands(age_band, lower_age, upper_age, sort_order) as (
    values
        ('0-20', 0, 20, 1),
        ('21-29', 21, 29, 2),
        ('30-39', 30, 39, 3),
        ('40-49', 40, 49, 4),
        ('50-59', 50, 59, 5),
        ('60+', 60, null, 6),
        ('Family/Other', null, null, 99)
)

select
    md5(age_band) as age_band_key,
    age_band,
    lower_age,
    upper_age,
    sort_order
from age_bands
