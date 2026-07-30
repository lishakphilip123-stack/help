"""One-time script: adds follow_up_questions and immediate_actions to the ontology CSV."""
import csv, os

ADDITIONS = {
    ("Structural Collapse or Severe Fire", "Partial Building Collapse"): {
        "follow_up_questions": "Is anyone trapped under rubble? | Which part of the building collapsed (wall/floor/ceiling)? | Is the rest of the structure still standing? | Are there gas or electrical lines exposed?",
        "immediate_actions": "Evacuate the building immediately | Do not re-enter | Call Fire and Rescue | Keep people away from the collapse zone | Shut off gas if safe to do so",
    },
    ("Structural Collapse or Severe Fire", "Full Building Collapse"): {
        "follow_up_questions": "Are there people confirmed trapped? | How many floors did the building have? | Is the collapse still ongoing? | Are there gas leaks or fires visible?",
        "immediate_actions": "Call emergency services immediately | Evacuate the entire area | Do not attempt rescue without USAR team | Mark last known positions of trapped people",
    },
    ("Structural Collapse or Severe Fire", "High-Rise Fire"): {
        "follow_up_questions": "Which floor is the fire on? | Are people trapped above the fire? | Is the stairwell accessible? | Is the fire spreading to other floors?",
        "immediate_actions": "Do not use elevators | Evacuate via stairwell below the fire floor | Close doors to slow fire spread | Call Fire and Rescue | Move to roof only as last resort",
    },
    ("Structural Collapse or Severe Fire", "Residential Fire"): {
        "follow_up_questions": "Is anyone still inside the building? | Is the fire in the kitchen, bedroom, or elsewhere? | Is the gas supply on? | Can you safely exit?",
        "immediate_actions": "Evacuate immediately | Close doors behind you | Call fire services | Do not go back inside | Meet at a safe distance outside",
    },
    ("Structural Collapse or Severe Fire", "Industrial or Warehouse Fire"): {
        "follow_up_questions": "Are hazardous chemicals stored on site? | Are workers unaccounted for? | Is the fire near fuel or gas storage? | Has the site been evacuated?",
        "immediate_actions": "Trigger site evacuation alarm | Call Fire and HAZMAT | Keep all personnel upwind | Do not attempt to fight chemical fires | Secure site perimeter",
    },
    ("Structural Collapse or Severe Fire", "Gas or Electrical Fire"): {
        "follow_up_questions": "Is the gas supply still on? | Is the electrical panel accessible to shut off? | Is the fire spreading? | Are there sparks or arcing wires visible?",
        "immediate_actions": "Do not use water on electrical fire | Shut off gas at the meter if safe | Evacuate and call Fire services | Do not touch exposed wiring",
    },
    ("Structural Collapse or Severe Fire", "Wildfire or Vegetation Fire"): {
        "follow_up_questions": "How close is the fire to homes or buildings? | Which direction is the wind blowing? | Is the road out still clear? | Are there people who cannot evacuate?",
        "immediate_actions": "Evacuate immediately if ordered | Close all windows and doors | Move to a cleared area or road | Do not shelter in a vehicle in the fire path",
    },
    ("Structural Collapse or Severe Fire", "Explosion"): {
        "follow_up_questions": "Was the explosion inside a building or outside? | Are there secondary fires or gas leaks? | Are people injured or trapped? | Was it a gas explosion or suspected device?",
        "immediate_actions": "Move away from the blast area | Do not re-enter the building | Call emergency services | Watch for secondary explosions | Do not use mobile phones near gas leaks",
    },
    ("Hazardous Chemical Leak or Toxic Gas Release", "Toxic Gas Leak"): {
        "follow_up_questions": "What is the source of the gas (industrial, domestic, vehicle)? | Can you smell or see the gas? | Are people showing symptoms (dizziness, breathing difficulty)? | Is the area evacuated?",
        "immediate_actions": "Move upwind immediately | Do not breathe the fumes | Call HAZMAT and emergency services | Cover mouth and nose | Do not use open flames or switches",
    },
    ("Hazardous Chemical Leak or Toxic Gas Release", "Flammable Vapour Leak"): {
        "follow_up_questions": "What is the source (LPG, petrol, natural gas)? | Is there an ignition source nearby? | How large is the affected area? | Is the leak still ongoing?",
        "immediate_actions": "Evacuate and keep away from ignition sources | Do not switch on/off any electrical devices | Call Gas Utility and Fire services | Ventilate if safe to do so",
    },
    ("Hazardous Chemical Leak or Toxic Gas Release", "Corrosive Chemical Spill"): {
        "follow_up_questions": "What chemical was spilled (acid, alkali, bleach)? | Has anyone been exposed or burned? | Is the spill contained or spreading? | Is it near a drain or water source?",
        "immediate_actions": "Do not touch the spill | Flush exposed skin with large amounts of water | Call HAZMAT | Contain the spill if safe | Keep people away",
    },
    ("Hazardous Chemical Leak or Toxic Gas Release", "Tanker or Transport Spill"): {
        "follow_up_questions": "What substance is the tanker carrying? | Is the vehicle on fire? | Is the spill reaching drains or waterways? | Is traffic stopped?",
        "immediate_actions": "Keep 300m distance | Call HAZMAT and Police | Do not allow vehicles through | Move upwind | Alert environmental authority if near water",
    },
    ("Hazardous Chemical Leak or Toxic Gas Release", "Laboratory Incident"): {
        "follow_up_questions": "What type of lab (school, hospital, research)? | What chemical or agent was involved? | Are people injured or exposed? | Is the lab sealed?",
        "immediate_actions": "Evacuate the lab and adjacent rooms | Seal the lab if possible | Call HAZMAT and facility emergency team | Do not touch any spilled material",
    },
    ("Hazardous Chemical Leak or Toxic Gas Release", "Radiation or Nuclear Incident"): {
        "follow_up_questions": "What is the source of radiation (plant, transport, device)? | Are people showing radiation sickness symptoms? | Has an official warning been issued? | What is the distance from the source?",
        "immediate_actions": "Move as far away as possible | Shelter indoors if evacuation not possible | Close all windows and doors | Do not consume local food or water | Await official instructions",
    },
    ("Hazardous Chemical Leak or Toxic Gas Release", "Biohazard or Infectious Outbreak"): {
        "follow_up_questions": "What is the suspected agent or disease? | How many people are showing symptoms? | Is the source known (lab, animal, person)? | Is the area quarantined?",
        "immediate_actions": "Isolate affected individuals | Call Public Health Authority | Avoid contact with bodily fluids | Wear mask and gloves if available | Do not leave the quarantine zone",
    },
    ("Flash Flooding and Infrastructure Failure", "Urban Flash Flood"): {
        "follow_up_questions": "Is water still rising? | Are people trapped in homes or vehicles? | Is the road out accessible? | Are there downed power lines in the water?",
        "immediate_actions": "Move to higher ground immediately | Do not walk or drive through floodwater | Turn off electricity at the mains | Call Disaster Management | Stay away from drains and rivers",
    },
    ("Flash Flooding and Infrastructure Failure", "People or Vehicles Stranded in Water"): {
        "follow_up_questions": "How many people are stranded? | Is the water still rising or moving fast? | Are they in a vehicle or on foot? | What is their exact location?",
        "immediate_actions": "Call Water Rescue immediately | Do not enter fast-moving water to help | Keep the stranded person calm and visible | Throw a rope or flotation device if available",
    },
    ("Flash Flooding and Infrastructure Failure", "Road or Bridge Washout"): {
        "follow_up_questions": "Is the road or bridge completely impassable? | Are vehicles or people on the damaged section? | Is water still flowing over it? | What is the location?",
        "immediate_actions": "Block access to the damaged road or bridge | Call Public Works and Police | Do not attempt to cross | Redirect traffic | Report exact GPS location",
    },
    ("Flash Flooding and Infrastructure Failure", "Drain or Sewer Overflow"): {
        "follow_up_questions": "Is sewage visible on the street? | Is it entering homes or buildings? | How widespread is the overflow? | Is it near a school or hospital?",
        "immediate_actions": "Avoid contact with floodwater (sewage contamination) | Call Water and Sanitation Authority | Keep children away | Disinfect any exposed surfaces",
    },
    ("Flash Flooding and Infrastructure Failure", "Power Infrastructure Failure"): {
        "follow_up_questions": "Is the outage affecting a single building or a wider area? | Are there downed power lines? | Is critical infrastructure (hospital, water plant) affected? | Was it caused by flooding or storm?",
        "immediate_actions": "Do not touch downed power lines | Call Electric Utility | Use torches not candles | Unplug sensitive equipment | Check on vulnerable neighbours",
    },
    ("Flash Flooding and Infrastructure Failure", "Water Supply Failure"): {
        "follow_up_questions": "Is there no water at all or just low pressure? | Is the water discoloured or smelling? | How many households are affected? | Is a hospital or care facility impacted?",
        "immediate_actions": "Use bottled water for drinking | Do not drink tap water if contaminated | Call Water Authority | Conserve existing water supply",
    },
    ("Flash Flooding and Infrastructure Failure", "Dam or Levee Breach"): {
        "follow_up_questions": "Has an official breach warning been issued? | How far downstream are you? | Is evacuation already underway? | Are roads out still open?",
        "immediate_actions": "Evacuate immediately to high ground | Do not wait for official order if water is rising | Call Disaster Management | Do not attempt to cross flooded roads",
    },
    ("Flash Flooding and Infrastructure Failure", "Landslide or Mudslide"): {
        "follow_up_questions": "Is the slide still moving? | Are people or buildings buried? | Is the road blocked? | Is there a risk of further slides (ongoing rain, unstable slope)?",
        "immediate_actions": "Move away from the slide path | Call Disaster Management and Fire and Rescue | Do not attempt to dig out victims without USAR | Watch for secondary slides",
    },
    ("Major Public Transit Disaster", "Train Derailment"): {
        "follow_up_questions": "Is the train carrying passengers or freight? | Are there casualties? | Is the train on fire or leaking fuel? | Is the track near a populated area?",
        "immediate_actions": "Call Rail Control and Emergency Services | Evacuate passengers away from the train | Do not move seriously injured passengers | Keep clear of the track",
    },
    ("Major Public Transit Disaster", "Train Collision"): {
        "follow_up_questions": "How many trains were involved? | Are there casualties? | Is there a fire? | Is the collision in a tunnel or open track?",
        "immediate_actions": "Call Rail Control and Emergency Services | Evacuate passengers | Administer first aid if trained | Keep the area clear for emergency vehicles",
    },
    ("Major Public Transit Disaster", "Metro or Tunnel Incident"): {
        "follow_up_questions": "Is there smoke or fire in the tunnel? | Are passengers evacuating or trapped? | Is the power to the track switched off? | Which station or tunnel section?",
        "immediate_actions": "Move away from smoke | Do not use elevators | Follow emergency lighting to exits | Call Transit Control | Do not walk on the track unless instructed",
    },
    ("Major Public Transit Disaster", "Major Bus Crash"): {
        "follow_up_questions": "How many passengers were on board? | Are there casualties? | Is the bus on fire or blocking traffic? | Is it a school bus?",
        "immediate_actions": "Call emergency services | Do not move seriously injured passengers | Keep traffic away | Administer first aid if trained | Secure the scene",
    },
    ("Major Public Transit Disaster", "Station Fire or Evacuation"): {
        "follow_up_questions": "Which station and which part (platform, concourse)? | Is the fire spreading? | Are passengers evacuating? | Is anyone trapped?",
        "immediate_actions": "Evacuate via nearest exit | Do not use elevators | Follow staff instructions | Call Fire and Rescue | Move away from the station entrance",
    },
    ("Major Public Transit Disaster", "Transit Vehicle in Water"): {
        "follow_up_questions": "Is the vehicle fully submerged or partially? | Are passengers still inside? | Is the water still rising? | What is the exact location?",
        "immediate_actions": "Call Water Rescue immediately | Do not enter the water unless trained | Break windows only if doors cannot open | Keep passengers calm and together",
    },
    ("Major Public Transit Disaster", "Aviation Incident"): {
        "follow_up_questions": "Has the aircraft crashed or made an emergency landing? | Is there a fire? | How many people were on board? | What is the location?",
        "immediate_actions": "Call Aviation Authority and Emergency Services | Keep clear of the crash site | Do not approach fuel spills | Follow airport emergency procedures if at airport",
    },
    ("Mass Casualty and Public Safety Incident", "Mass Casualty Event"): {
        "follow_up_questions": "What caused the casualties (accident, attack, collapse)? | How many people are injured? | Is the scene still dangerous? | Is medical help on the way?",
        "immediate_actions": "Call emergency services immediately | Do not move critically injured people | Apply pressure to bleeding wounds | Keep the area clear for ambulances | Triage: help those who can be saved first",
    },
    ("Mass Casualty and Public Safety Incident", "Terrorist Attack or Bombing"): {
        "follow_up_questions": "Was it an explosion, shooting, or vehicle attack? | Is the attacker still active? | Are there secondary devices? | What is the location?",
        "immediate_actions": "Run, Hide, Tell — evacuate if safe | Do not touch suspicious objects | Call Police immediately | Stay low if there is shooting | Do not return to the scene",
    },
    ("Mass Casualty and Public Safety Incident", "Active Shooter or Armed Threat"): {
        "follow_up_questions": "Where is the shooter now? | Are you in a safe location? | How many people are with you? | Is anyone injured?",
        "immediate_actions": "Run if you can escape safely | Hide and barricade if you cannot run | Stay silent — silence your phone | Call Police when safe | Do not confront the shooter",
    },
    ("Mass Casualty and Public Safety Incident", "Crowd Crush or Stampede"): {
        "follow_up_questions": "Are you currently in the crowd? | Is the crowd still moving or has it stopped? | Are people falling? | Is there an exit nearby?",
        "immediate_actions": "Move sideways to the edge of the crowd | Do not fight the crowd flow | Protect your chest — keep arms up | Call for help when clear | Help fallen people only when safe",
    },
    ("Mass Casualty and Public Safety Incident", "Missing Person or Search and Rescue"): {
        "follow_up_questions": "How long has the person been missing? | What is their age and physical description? | Where were they last seen? | Do they have a medical condition?",
        "immediate_actions": "Call Police immediately | Do not disturb the last known location | Share a recent photo | Search nearby areas in groups | Keep phone charged and on",
    },
    ("Natural Disaster", "Earthquake"): {
        "follow_up_questions": "Are you currently indoors or outdoors? | Is the shaking still happening? | Are there structural damages or collapses nearby? | Are gas or water lines broken?",
        "immediate_actions": "Drop, Cover, Hold On during shaking | Move away from buildings after shaking stops | Check for gas leaks — do not use flames | Expect aftershocks | Call Disaster Management",
    },
    ("Natural Disaster", "Tsunami"): {
        "follow_up_questions": "Have you felt an earthquake or received a tsunami warning? | How far are you from the coast? | Is the sea receding unusually? | Is evacuation underway?",
        "immediate_actions": "Move inland and to high ground immediately | Do not wait to see the wave | Do not return to the coast until all-clear | Follow official evacuation routes",
    },
    ("Natural Disaster", "Severe Storm or Cyclone"): {
        "follow_up_questions": "Has an official warning been issued? | Are you in a safe structure? | Are there downed power lines or flooding? | Do you need to evacuate?",
        "immediate_actions": "Stay indoors away from windows | Secure loose outdoor objects | Have emergency kit ready | Monitor official weather updates | Evacuate if in a flood-prone area",
    },
    ("Natural Disaster", "Extreme Heat Event"): {
        "follow_up_questions": "Is anyone showing signs of heat stroke (confusion, no sweating, high temperature)? | Do you have access to water and shade? | Are vulnerable people (elderly, children) affected?",
        "immediate_actions": "Move to a cool or air-conditioned space | Drink water regularly | Apply cool wet cloths to heat stroke victims | Call ambulance for heat stroke — it is life-threatening | Avoid outdoor activity",
    },
    ("Natural Disaster", "Blizzard or Ice Storm"): {
        "follow_up_questions": "Are you stranded outdoors or in a vehicle? | Is visibility near zero? | Do you have heating and supplies? | Are roads closed?",
        "immediate_actions": "Stay indoors | Do not drive unless essential | Keep emergency supplies (food, water, blankets) | Check on elderly neighbours | Call Public Works if roads are blocked",
    },
    ("Utility and Infrastructure Emergency", "Gas Main Rupture"): {
        "follow_up_questions": "Can you hear or smell gas outside? | Is there a visible crack or hissing pipe? | Are buildings nearby? | Has the area been evacuated?",
        "immediate_actions": "Evacuate the area immediately | Do not use any electrical switches or flames | Call Gas Utility and Fire services | Keep people 200m away | Do not attempt to repair",
    },
    ("Utility and Infrastructure Emergency", "Major Power Grid Failure"): {
        "follow_up_questions": "How large is the affected area (street, district, city)? | Is critical infrastructure (hospital, water plant) affected? | Is it storm-related? | How long has it been out?",
        "immediate_actions": "Use backup power for critical equipment | Do not touch downed lines | Call Electric Utility | Conserve phone battery | Check on vulnerable people",
    },
    ("Utility and Infrastructure Emergency", "Telecommunications Failure"): {
        "follow_up_questions": "Is it mobile, internet, or both? | Is emergency services communication affected? | How wide is the outage? | Is it storm or infrastructure related?",
        "immediate_actions": "Use landline if available | Move to an area with signal | Use radio for emergency broadcasts | Report to nearest emergency services office if critical",
    },
    ("Utility and Infrastructure Emergency", "Bridge or Road Structural Failure"): {
        "follow_up_questions": "Is the failure sudden (collapse) or gradual (cracks, sinking)? | Are vehicles or people on the structure? | Is it a major route? | What is the location?",
        "immediate_actions": "Stop all traffic immediately | Call Public Works and Police | Keep people away from the structure | Do not attempt to cross | Report exact location",
    },
    ("Utility and Infrastructure Emergency", "Water Main Burst"): {
        "follow_up_questions": "Is water gushing onto the road? | Is it causing road flooding or subsidence? | Is the water supply cut to buildings? | What is the location?",
        "immediate_actions": "Call Water Authority immediately | Avoid the flooded road area | Do not drive through water over a burst main (road may collapse) | Report exact location",
    },
    ("Marine and Coastal Emergency", "Vessel in Distress"): {
        "follow_up_questions": "What type of vessel (ship, boat, ferry)? | How many people are on board? | Is the vessel sinking or on fire? | What is the GPS position or nearest landmark?",
        "immediate_actions": "Send MAYDAY on VHF Channel 16 | Deploy life jackets and life rafts | Call Coast Guard | Activate EPIRB if available | Stay with the vessel unless sinking",
    },
    ("Marine and Coastal Emergency", "Oil or Chemical Spill at Sea"): {
        "follow_up_questions": "What substance was spilled? | How large is the slick? | Is it near a coastline or marine reserve? | Is the source vessel still leaking?",
        "immediate_actions": "Call Coast Guard and Environmental Authority | Do not attempt to clean up without HAZMAT | Keep vessels away from the spill | Report GPS coordinates",
    },
    ("Marine and Coastal Emergency", "Coastal Flooding"): {
        "follow_up_questions": "Is the flooding from a storm surge or high tide? | How far inland is the water? | Are people trapped in coastal buildings? | Is evacuation underway?",
        "immediate_actions": "Move inland and to higher ground | Do not drive through coastal floodwater | Call Disaster Management | Monitor official coastal warnings | Help vulnerable people evacuate",
    },
}

src = "data/emergency_ontology_v2.csv"
dst = "data/emergency_ontology_v2.csv"

rows = list(csv.DictReader(open(src, encoding="utf-8")))
fieldnames = list(rows[0].keys()) + ["follow_up_questions", "immediate_actions"]

for row in rows:
    key = (row["category"], row["subcategory"])
    extra = ADDITIONS.get(key, {})
    row["follow_up_questions"] = extra.get("follow_up_questions", "")
    row["immediate_actions"] = extra.get("immediate_actions", "")

with open(dst, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Done. {len(rows)} rows updated.")
