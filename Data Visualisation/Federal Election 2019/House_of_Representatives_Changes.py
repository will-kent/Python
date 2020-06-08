import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
import seaborn as sns

# From AEC of federal election results
data = {"party": ["Liberal-National Coalition","Australian Labor Party", "Other",
                  "Liberal-National Coalition","Australian Labor Party", "Other"],
       "election_year": ["2016","2016","2016","2019","2019","2019"],
       "seats": [76,69,5,77,68,6]}

df = pd.DataFrame(data)
df.head()
df.info()

party_values = df.loc[:, "party"].values

fig, axes = plt.subplots(nrows = 1, ncols = 1, figsize = (2,4))

for party in np.unique(party_values):
    seats = df.loc[df["party"] == party, "seats"].values
    year = df.loc[df["party"] == party, "election_year"].values
    if party == "Australian Labor Party":
        party_colour = "#DE3533"
    elif party == "Liberal-National Coalition":
        party_colour = "#0047AB"
    else:
        party_colour = "#c7c5d1"
    axes.plot(year, seats, c = party_colour, linewidth = 4)
    axes.scatter(year, seats, s = 100,c = party_colour)

#Set Labels
axes.set_xlabel("Election Year", fontsize = 12)
axes.set_ylabel("Seats Won", fontsize = 12)

axes.yaxis.set_ticks(np.arange(0, 85, 20))

#Remove tick marks
axes.tick_params(length = 0)

#Remove spines
axes.spines["right"].set_visible(False)
axes.spines["left"].set_visible(False)
axes.spines["top"].set_visible(False)
axes.spines["bottom"].set_visible(False)

fig.savefig("house_seats.png", dpi = 300)




