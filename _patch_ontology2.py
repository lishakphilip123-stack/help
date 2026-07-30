"""One-time script: adds escalation_triggers, max_followup_questions, cascade_to to the ontology CSV."""
import csv

ADDITIONS = {
    ("Structural Collapse or Severe Fire", "Partial Building Collapse"): {
        "escalation_triggers": "trapped, buried, rubble, people inside, workers inside, residents inside",
        "max_followup_questions": "2",
        "cascade_to": "",
    },
    ("Structural Collapse or Severe Fire", "Full Building Collapse"): {
        "escalation_triggers": "trapped, buried, people inside, multiple, many, casualties, dead, dying",
        "max_followup_questions": "1",
        "cascade_to": "Gas Main Rupture; Mass Casualty Event",
    },
    ("Structural Collapse or Severe Fire", "High-Rise Fire"): {
        "escalation_triggers": "trapped, people inside, multiple floors, spreading, casualties",
        "max_followup_questions": "2",
        "cascade_to": "",
    },
    ("Structural Collapse or Severe Fire", "Residential Fire"): {
        "escalation_triggers": "trapped, inside, child, baby, elderly, unconscious, not moving",
        "max_followup_questions": "2",
        "cascade_to": "",
    },
    ("Structural Collapse or Severe Fire", "Industrial or Warehouse Fire"): {
        "escalation_triggers": "workers trapped, chemical, explosion, casualties, multiple injured",
        "max_followup_questions": "2",
        "cascade_to": "Toxic Gas Leak; Corrosive Chemical Spill",
    },
    ("Structural Collapse or Severe Fire", "Gas or Electrical Fire"): {
        "escalation_triggers": "explosion, spreading fast, multiple rooms, casualties",
        "max_followup_questions": "2",
        "cascade_to": "Gas Main Rupture",
    },
    ("Structural Collapse or Severe Fire", "Wildfire or Vegetation Fire"): {
        "escalation_triggers": "surrounded, cut off, cannot evacuate, people trapped, spreading fast, homes burning",
        "max_followup_questions": "2",
        "cascade_to": "",
    },
    ("Structural Collapse or Severe Fire", "Explosion"): {
        "escalation_triggers": "casualties, injured, trapped, multiple, dead, dying, bomb, device",
        "max_followup_questions": "1",
        "cascade_to": "Mass Casualty Event; Toxic Gas Leak",
    },
    ("Hazardous Chemical Leak or Toxic Gas Release", "Toxic Gas Leak"): {
        "escalation_triggers": "unconscious, not breathing, symptoms, exposed, multiple people, casualties, collapsed",
        "max_followup_questions": "2",
        "cascade_to": "",
    },
    ("Hazardous Chemical Leak or Toxic Gas Release", "Flammable Vapour Leak"): {
        "escalation_triggers": "ignition, fire, explosion, spreading, large area",
        "max_followup_questions": "2",
        "cascade_to": "Gas or Electrical Fire",
    },
    ("Hazardous Chemical Leak or Toxic Gas Release", "Corrosive Chemical Spill"): {
        "escalation_triggers": "burned, skin burn, exposed, multiple people, casualties, eyes",
        "max_followup_questions": "2",
        "cascade_to": "",
    },
    ("Hazardous Chemical Leak or Toxic Gas Release", "Tanker or Transport Spill"): {
        "escalation_triggers": "fire, explosion, casualties, river, water supply, large spill, spreading",
        "max_followup_questions": "2",
        "cascade_to": "Toxic Gas Leak; Oil or Chemical Spill at Sea",
    },
    ("Hazardous Chemical Leak or Toxic Gas Release", "Laboratory Incident"): {
        "escalation_triggers": "exposed, casualties, fire, explosion, biohazard, radiation",
        "max_followup_questions": "2",
        "cascade_to": "Biohazard or Infectious Outbreak",
    },
    ("Hazardous Chemical Leak or Toxic Gas Release", "Radiation or Nuclear Incident"): {
        "escalation_triggers": "exposed, symptoms, nausea, vomiting, radiation sickness, multiple people, casualties",
        "max_followup_questions": "1",
        "cascade_to": "",
    },
    ("Hazardous Chemical Leak or Toxic Gas Release", "Biohazard or Infectious Outbreak"): {
        "escalation_triggers": "multiple sick, spreading, casualties, deaths, hospital overwhelmed, quarantine breach",
        "max_followup_questions": "2",
        "cascade_to": "",
    },
    ("Flash Flooding and Infrastructure Failure", "Urban Flash Flood"): {
        "escalation_triggers": "trapped, swept away, drowning, people in water, rising fast, casualties, children",
        "max_followup_questions": "2",
        "cascade_to": "People or Vehicles Stranded in Water; Power Infrastructure Failure",
    },
    ("Flash Flooding and Infrastructure Failure", "People or Vehicles Stranded in Water"): {
        "escalation_triggers": "drowning, swept away, sinking, submerged, multiple, passengers, children, elderly, casualties",
        "max_followup_questions": "1",
        "cascade_to": "",
    },
    ("Flash Flooding and Infrastructure Failure", "Road or Bridge Washout"): {
        "escalation_triggers": "vehicle fell, people on bridge, casualties, swept away",
        "max_followup_questions": "2",
        "cascade_to": "People or Vehicles Stranded in Water",
    },
    ("Flash Flooding and Infrastructure Failure", "Drain or Sewer Overflow"): {
        "escalation_triggers": "child fell, person in drain, casualties",
        "max_followup_questions": "3",
        "cascade_to": "",
    },
    ("Flash Flooding and Infrastructure Failure", "Power Infrastructure Failure"): {
        "escalation_triggers": "hospital, life support, electrocution, downed lines, casualties",
        "max_followup_questions": "3",
        "cascade_to": "",
    },
    ("Flash Flooding and Infrastructure Failure", "Water Supply Failure"): {
        "escalation_triggers": "hospital, dialysis, contaminated, sick, casualties",
        "max_followup_questions": "4",
        "cascade_to": "",
    },
    ("Flash Flooding and Infrastructure Failure", "Dam or Levee Breach"): {
        "escalation_triggers": "breached, collapsed, water rushing, downstream flooding, casualties, trapped",
        "max_followup_questions": "1",
        "cascade_to": "Urban Flash Flood; People or Vehicles Stranded in Water",
    },
    ("Flash Flooding and Infrastructure Failure", "Landslide or Mudslide"): {
        "escalation_triggers": "buried, trapped, casualties, house buried, people missing",
        "max_followup_questions": "2",
        "cascade_to": "Partial Building Collapse",
    },
    ("Major Public Transit Disaster", "Train Derailment"): {
        "escalation_triggers": "passengers, casualties, injured, trapped, fire, multiple, derailed",
        "max_followup_questions": "2",
        "cascade_to": "Mass Casualty Event",
    },
    ("Major Public Transit Disaster", "Train Collision"): {
        "escalation_triggers": "casualties, injured, trapped, fire, multiple, passengers",
        "max_followup_questions": "1",
        "cascade_to": "Mass Casualty Event",
    },
    ("Major Public Transit Disaster", "Metro or Tunnel Incident"): {
        "escalation_triggers": "smoke, fire, trapped, casualties, power on, passengers stuck",
        "max_followup_questions": "2",
        "cascade_to": "Mass Casualty Event",
    },
    ("Major Public Transit Disaster", "Major Bus Crash"): {
        "escalation_triggers": "casualties, injured, trapped, fire, multiple, passengers, school bus, children",
        "max_followup_questions": "2",
        "cascade_to": "Mass Casualty Event",
    },
    ("Major Public Transit Disaster", "Station Fire or Evacuation"): {
        "escalation_triggers": "trapped, casualties, stampede, crush, multiple, spreading",
        "max_followup_questions": "2",
        "cascade_to": "Crowd Crush or Stampede",
    },
    ("Major Public Transit Disaster", "Transit Vehicle in Water"): {
        "escalation_triggers": "passengers, drowning, submerged, sinking, trapped, multiple, children, water rising",
        "max_followup_questions": "1",
        "cascade_to": "People or Vehicles Stranded in Water; Mass Casualty Event",
    },
    ("Major Public Transit Disaster", "Aviation Incident"): {
        "escalation_triggers": "crashed, fire, casualties, passengers, multiple, explosion",
        "max_followup_questions": "1",
        "cascade_to": "Mass Casualty Event",
    },
    ("Mass Casualty and Public Safety Incident", "Mass Casualty Event"): {
        "escalation_triggers": "multiple, many, casualties, dead, dying, injured, mass, crowd",
        "max_followup_questions": "1",
        "cascade_to": "",
    },
    ("Mass Casualty and Public Safety Incident", "Terrorist Attack or Bombing"): {
        "escalation_triggers": "bomb, explosion, shooting, attack, casualties, dead, injured, device",
        "max_followup_questions": "1",
        "cascade_to": "Active Shooter or Armed Threat; Mass Casualty Event",
    },
    ("Mass Casualty and Public Safety Incident", "Active Shooter or Armed Threat"): {
        "escalation_triggers": "shooter, gunfire, shots, armed, hostage, weapon, attack",
        "max_followup_questions": "1",
        "cascade_to": "",
    },
    ("Mass Casualty and Public Safety Incident", "Crowd Crush or Stampede"): {
        "escalation_triggers": "falling, trampled, crush, cannot breathe, people down, casualties",
        "max_followup_questions": "1",
        "cascade_to": "Mass Casualty Event",
    },
    ("Mass Casualty and Public Safety Incident", "Missing Person or Search and Rescue"): {
        "escalation_triggers": "child, baby, dementia, medical condition, water, cliff, wilderness, night",
        "max_followup_questions": "3",
        "cascade_to": "",
    },
    ("Natural Disaster", "Earthquake"): {
        "escalation_triggers": "trapped, building collapsed, casualties, gas smell, fire, multiple, buried",
        "max_followup_questions": "2",
        "cascade_to": "Partial Building Collapse; Gas Main Rupture; Landslide or Mudslide; Tsunami",
    },
    ("Natural Disaster", "Tsunami"): {
        "escalation_triggers": "wave coming, sea receding, warning issued, wave seen, coastal, flooding",
        "max_followup_questions": "1",
        "cascade_to": "Coastal Flooding; People or Vehicles Stranded in Water",
    },
    ("Natural Disaster", "Severe Storm or Cyclone"): {
        "escalation_triggers": "roof gone, trapped, casualties, flooding, power lines down, cannot evacuate",
        "max_followup_questions": "2",
        "cascade_to": "Urban Flash Flood; Power Infrastructure Failure",
    },
    ("Natural Disaster", "Extreme Heat Event"): {
        "escalation_triggers": "heat stroke, unconscious, not sweating, confusion, collapsed, casualties, elderly, child",
        "max_followup_questions": "2",
        "cascade_to": "",
    },
    ("Natural Disaster", "Blizzard or Ice Storm"): {
        "escalation_triggers": "stranded, hypothermia, unconscious, casualties, trapped, no heat, freezing",
        "max_followup_questions": "2",
        "cascade_to": "Power Infrastructure Failure",
    },
    ("Utility and Infrastructure Emergency", "Gas Main Rupture"): {
        "escalation_triggers": "fire, explosion, casualties, large area, multiple buildings, hissing loud",
        "max_followup_questions": "2",
        "cascade_to": "Gas or Electrical Fire; Explosion",
    },
    ("Utility and Infrastructure Emergency", "Major Power Grid Failure"): {
        "escalation_triggers": "hospital, life support, traffic lights, wide area, city, casualties",
        "max_followup_questions": "3",
        "cascade_to": "",
    },
    ("Utility and Infrastructure Emergency", "Telecommunications Failure"): {
        "escalation_triggers": "emergency services down, cannot call 911, no comms, widespread",
        "max_followup_questions": "3",
        "cascade_to": "",
    },
    ("Utility and Infrastructure Emergency", "Bridge or Road Structural Failure"): {
        "escalation_triggers": "vehicle fell, people on bridge, casualties, collapsed, sinking",
        "max_followup_questions": "1",
        "cascade_to": "People or Vehicles Stranded in Water; Mass Casualty Event",
    },
    ("Utility and Infrastructure Emergency", "Water Main Burst"): {
        "escalation_triggers": "road collapsing, sinkhole, vehicle fell, casualties, flooding fast",
        "max_followup_questions": "3",
        "cascade_to": "Urban Flash Flood",
    },
    ("Marine and Coastal Emergency", "Vessel in Distress"): {
        "escalation_triggers": "sinking, capsized, fire, mayday, passengers, multiple, drowning, casualties",
        "max_followup_questions": "1",
        "cascade_to": "People or Vehicles Stranded in Water; Mass Casualty Event",
    },
    ("Marine and Coastal Emergency", "Oil or Chemical Spill at Sea"): {
        "escalation_triggers": "fire, explosion, casualties, large spill, coastline, drinking water",
        "max_followup_questions": "2",
        "cascade_to": "Toxic Gas Leak",
    },
    ("Marine and Coastal Emergency", "Coastal Flooding"): {
        "escalation_triggers": "trapped, swept away, drowning, casualties, multiple, rising fast",
        "max_followup_questions": "2",
        "cascade_to": "People or Vehicles Stranded in Water; Urban Flash Flood",
    },
}

src = "data/emergency_ontology_v2.csv"
rows = list(csv.DictReader(open(src, encoding="utf-8")))
fieldnames = list(rows[0].keys()) + ["escalation_triggers", "max_followup_questions", "cascade_to"]

for row in rows:
    key = (row["category"], row["subcategory"])
    extra = ADDITIONS.get(key, {})
    row["escalation_triggers"] = extra.get("escalation_triggers", "")
    row["max_followup_questions"] = extra.get("max_followup_questions", "3")
    row["cascade_to"] = extra.get("cascade_to", "")

with open(src, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Done. {len(rows)} rows updated.")
