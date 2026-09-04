import os
import json
import math
import urllib.request
from datetime import datetime, timezone

USERNAME = "imandeepduhan"
TOKEN = os.environ["GITHUB_TOKEN"]

now = datetime.now(timezone.utc)
start = datetime(now.year, 1, 1, tzinfo=timezone.utc)

query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
    }
  }
}
"""

payload = json.dumps({
    "query": query,
    "variables": {
        "login": USERNAME,
        "from": start.isoformat(),
        "to": now.isoformat()
    }
}).encode()

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "github-activity"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read())

data = result["data"]["user"]["contributionsCollection"]

commits = data["totalCommitContributions"]
issues = data["totalIssueContributions"]
pull_requests = data["totalPullRequestContributions"]
reviews = data["totalPullRequestReviewContributions"]

total = commits + issues + pull_requests + reviews

if total == 0:
    percentages = {
        "Commits": 0,
        "Issues": 0,
        "Pull requests": 0,
        "Code review": 0
    }
else:
    percentages = {
        "Commits": round(commits * 100 / total),
        "Issues": round(issues * 100 / total),
        "Pull requests": round(pull_requests * 100 / total),
        "Code review": round(reviews * 100 / total)
    }

# Fix rounding so total is exactly 100
difference = 100 - sum(percentages.values())

largest = max(percentages, key=percentages.get)
percentages[largest] += difference


# --------------------------------------------------
# SVG
# --------------------------------------------------

width = 650
height = 420

cx = 490
cy = 210

max_radius = 105

# Directions:
# Top    = Code review
# Right  = Issues
# Bottom = Pull requests
# Left   = Commits

values = [
    percentages["Code review"],
    percentages["Issues"],
    percentages["Pull requests"],
    percentages["Commits"]
]

labels = [
    "Code review",
    "Issues",
    "Pull requests",
    "Commits"
]

angles = [
    -math.pi / 2,
    0,
    math.pi / 2,
    math.pi
]


def point(angle, radius):
    x = cx + math.cos(angle) * radius
    y = cy + math.sin(angle) * radius
    return x, y


# Polygon points
polygon_points = []

for value, angle in zip(values, angles):
    radius = max_radius * value / 100
    x, y = point(angle, radius)
    polygon_points.append(f"{x:.2f},{y:.2f}")

polygon = " ".join(polygon_points)


svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}">

<rect x="0" y="0"
      width="{width}"
      height="{height}"
      rx="10"
      fill="#15191e"
      stroke="#3b424a"/>

<!-- Divider -->
<line x1="350" y1="35"
      x2="350" y2="385"
      stroke="#3b424a"/>

<!-- Graph axes -->
<line x1="{cx}" y1="{cy-max_radius}"
      x2="{cx}" y2="{cy+max_radius}"
      stroke="#45e05c"
      stroke-width="3"/>

<line x1="{cx-max_radius}" y1="{cy}"
      x2="{cx+max_radius}" y2="{cy}"
      stroke="#45e05c"
      stroke-width="3"/>


<!-- Activity polygon -->
<polygon points="{polygon}"
         fill="#45e05c"
         fill-opacity="0.35"
         stroke="#45e05c"
         stroke-width="3"/>


<!-- Center -->
<circle cx="{cx}" cy="{cy}"
        r="5"
        fill="#ffffff"/>


<!-- Points -->
"""

# Add points
for value, angle in zip(values, angles):

    radius = max_radius * value / 100

    x, y = point(angle, radius)

    svg += f"""
<circle cx="{x:.2f}"
        cy="{y:.2f}"
        r="5"
        fill="#15191e"
        stroke="#45e05c"
        stroke-width="3"/>
"""


svg += f"""

<!-- Top -->
<text x="{cx}"
      y="50"
      text-anchor="middle"
      fill="#8b949e"
      font-size="16">
    {percentages["Code review"]}%
</text>

<text x="{cx}"
      y="72"
      text-anchor="middle"
      fill="#8b949e"
      font-size="16">
    Code review
</text>


<!-- Right -->
<text x="{cx+125}"
      y="{cy-8}"
      text-anchor="start"
      fill="#8b949e"
      font-size="16">
    {percentages["Issues"]}%
</text>

<text x="{cx+125}"
      y="{cy+20}"
      text-anchor="start"
      fill="#8b949e"
      font-size="16">
    Issues
</text>


<!-- Bottom -->
<text x="{cx}"
      y="{cy+145}"
      text-anchor="middle"
      fill="#8b949e"
      font-size="16">
    {percentages["Pull requests"]}%
</text>

<text x="{cx}"
      y="{cy+168}"
      text-anchor="middle"
      fill="#8b949e"
      font-size="16">
    Pull requests
</text>


<!-- Left -->
<text x="{cx-125}"
      y="{cy-8}"
      text-anchor="end"
      fill="#8b949e"
      font-size="16">
    {percentages["Commits"]}%
</text>

<text x="{cx-125}"
      y="{cy+20}"
      text-anchor="end"
      fill="#8b949e"
      font-size="16">
    Commits
</text>


<!-- Title -->
<text x="25"
      y="45"
      fill="#ffffff"
      font-size="19">
    Activity overview
</text>

<text x="25"
      y="85"
      fill="#8b949e"
      font-size="15">
    GitHub activity
</text>

</svg>
"""

with open("activity-overview.svg", "w", encoding="utf-8") as file:
    file.write(svg)

print("Activity overview generated!")
print(percentages)
