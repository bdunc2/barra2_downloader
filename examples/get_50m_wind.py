from datetime import datetime, timezone
from barra2_downloader import params, model_domains, get_df_for_data

print ("Data for rss parameter")

print (get_df_for_data(
    model_domains.BARRAModel.BARRA_C2,
    model_domains.BARRADomain.AUST_04,
    model_domains.BARRAFrequency.min20,
    ["ua50m", "va50m"], # Get the 50m values for eastern and northern winds (50m from surface)
    datetime(2026, 3, 4, 13, 45, 0, tzinfo=timezone.utc),
    datetime(2026, 5, 25, 0, 0, 0, tzinfo=timezone.utc),
    latitude=-26.52267239,
    longitude=152.573373,
    verbose=True,
    threaded_download=True
))