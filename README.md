# CBBSIM Explainer
Information for college basketball similarity website

[current link](cbbsim.herokuapp.com)

This tool uses team-level advanced statistics from Ken Pomeroy and Bart Torvik to determine the closest historical comparisons to current men's college basketball team. Using current and past teams' metrics for overall power rating, offensive and defensive efficiency, as well as tempo, this project determines current teams' closest neighbors from past Selection Sundays, and then summarizes how these teams fared in march. (Note: historical years correspond to the year the tournament was held, ie 2008-09 season is 2009)

The chosen statistics offer a proxy for both team ability (overall power rating, offensive/defensive efficiency), as well as playstyle (off/def as well as tempo). Using a k-nearest neighbors model in Python, a weighted average (weights are 1/d, where d represents the four-dimensional Euclidean distance between regularized metrics) expected NCAA Tournament seed is constructed for teams. This model generally performs better with fewer parameters, hence limiting to only these four.

It is worth noting that these statistics aren't meant to be inherently predictive, and certainly don't incorporate enough context to make the best prediction for a team's ultimate seed. However, I think they offer a new and improved basis for evaluating how teams' advanced metrics are interpreted, benchmarked against past teams. Saying a team has +24 AdjEM, or 114 AdjO is a better basis for predicting future performance, but this tool essentially suggests "this team is playing like a 2 seed" or a bubble team - which hopefully makes Pomeroy/Torvik's work more interpretable, though I'd nonetheless recommend a deeper understanding of their work to anyone interested.

CBBSIM offers team pages dating back to 2002 (though teams from the early 2000s have some gaps in reliability), and highlights each team's nearest comparisons/suggested seed. Based on this, I thought I would summarize some interesting findings about the biggest snubs/most underseeded teams.

__*Biggest NCAAT Snubs*__

| __Team__               | __Suggested Seed__ |
|------------------------|----------------|
| Clemson2019            | 4.83           |
| Louisville2016*        | 4.87           |
| SMU2016*               | 5.31           |
| Penn St.2018           | 5.86           |
| Georgia2003*           | 5.96           |
| Oklahoma St.2018       | 6.55           |
| Saint Mary's2016       | 6.58           |
| Iowa2013               | 6.64           |
| South Carolina2002     | 6.86           |
| Florida St.2004        | 6.89           |
| North Carolina St.2019 | 6.93           |
| Clemson2017            | 7.00           |
| Louisville2018         | 7.03           |
| Syracuse2017           | 7.17           |
| Penn St.2019           | 7.20           |
| Virginia Tech2010      | 7.23           |
| Florida2016            | 7.29           |
| Texas2019              | 7.35           |
| USC2018                | 7.38           |
| Mississippi St.2007    | 7.47           |

\* *denotes teams with a postseason ban*


__*Most Underseeded NCAAT Teams*__

| __Team__              | __Suggested Seed__ | __Actual Seed__ | __Delta__ |
|-----------------------|----------------|-------------|-------|
| Utah St.2005          | 7.05           | 14          | -6.95 |
| Wichita St.2016       | 4.09           | 11          | -6.91 |
| Vanderbilt2016        | 4.33           | 11          | -6.67 |
| Wichita St.2017       | 3.43           | 10          | -6.57 |
| Utah St.2011          | 5.49           | 12          | -6.51 |
| Belmont2012           | 7.50           | 14          | -6.50 |
| Gonzaga2016           | 4.96           | 11          | -6.04 |
| Belmont2011           | 7.07           | 13          | -5.93 |
| Utah St.2010          | 6.16           | 12          | -5.84 |
| Tennessee2014         | 5.36           | 11          | -5.64 |
| Texas2015             | 5.46           | 11          | -5.54 |
| UTEP2010              | 6.53           | 12          | -5.47 |
| Ohio St.2015          | 4.61           | 10          | -5.39 |
| Bradley2006           | 7.74           | 13          | -5.26 |
| Stephen F. Austin2016 | 8.93           | 14          | -5.07 |
| Clemson2011           | 7.02           | 12          | -4.98 |
| BYU2015               | 6.14           | 11          | -4.86 |
| Washington2010        | 6.29           | 11          | -4.71 |
| Wisconsin2009         | 7.32           | 12          | -4.68 |
| Oklahoma St.2017      | 5.33           | 10          | -4.67 |
| Iowa2014              | 6.39           | 11          | -4.61 |
| Wake Forest2017       | 6.41           | 11          | -4.59 |
| Air Force2006         | 8.43           | 13          | -4.57 |
| Davidson2008          | 5.46           | 10          | -4.54 |
| Missouri2010          | 5.61           | 10          | -4.39 |
| Butler2018            | 5.65           | 10          | -4.35 |
| Kansas St.2008        | 6.68           | 11          | -4.32 |
| St. Bonaventure2012   | 9.76           | 14          | -4.24 |
| Saint Mary's2013      | 6.88           | 11          | -4.12 |
| Oregon2013            | 7.91           | 12          | -4.09 |__
