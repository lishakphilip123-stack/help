import json

data = {
  "scenarios": {
    "flood": {
      "tag": "flood", "label": "Flood Emergency", "icon": "\U0001f30a",
      "faqs": [
        {"q": "What should I do if my area is flooded?", "a": "Move immediately to higher ground. Do not walk or drive through floodwaters. Call emergency services at 112 if you are trapped. Take essential documents, medicines, and supplies."},
        {"q": "How do I prepare for a flood warning?", "a": "Stock emergency supplies (water, food, torch, first aid). Move valuables to upper floors. Know your nearest evacuation route and shelter. Keep your phone charged and monitor official alerts."},
        {"q": "Is it safe to drive through flooded roads?", "a": "No. Just 15 cm of fast-moving water can knock a person down, and 60 cm can sweep away a vehicle. Turn around, do not drown."},
        {"q": "Where are flood relief camps located?", "a": "Relief camps are set up at government schools, community halls, and stadiums. Contact your local municipal office or dial 1077 (State Disaster Helpline) for the nearest camp location."},
        {"q": "How do I report a flood emergency?", "a": "Call the National Emergency Number 112, State Disaster Helpline 1077, or contact your local fire and rescue services."},
        {"q": "What should I avoid during a flood?", "a": "Avoid walking in moving water, touching electrical equipment in wet areas, drinking tap water (may be contaminated), and returning home before authorities declare it safe."},
        {"q": "How do I stay safe if trapped in a flooded building?", "a": "Move to the highest floor. Signal rescuers using a torch or bright cloth from a window. Do not attempt to swim out. Call 112 and stay on the line."},
        {"q": "What do I do after floodwaters recede?", "a": "Do not return home until authorities confirm it is safe. Check for structural damage before entering. Use protective gear when cleaning. Boil water before drinking. Watch for snakes and insects."},
        {"q": "How do I protect my documents during a flood?", "a": "Store documents in waterproof bags or sealed plastic containers. Keep digital copies on cloud storage. Place them on upper shelves or take them with you during evacuation."},
        {"q": "What food and water should I store for a flood emergency?", "a": "Store at least 3 days of non-perishable food (canned goods, dry food) and 3 litres of water per person per day. Include a manual can opener and water purification tablets."},
        {"q": "How do I help elderly or disabled neighbours during a flood?", "a": "Check on them immediately. Help them evacuate to higher ground or a relief camp. Inform rescue teams of their location if you cannot assist them yourself."},
        {"q": "What is the flood warning colour code?", "a": "Green: No warning. Yellow: Watch (be prepared). Orange: Alert (be ready to act). Red: Warning (take immediate action). Follow instructions from local authorities for each level."}
      ]
    },
    "fire": {
      "tag": "fire", "label": "Fire Emergency", "icon": "\U0001f525",
      "faqs": [
        {"q": "What should I do if there is a fire in my building?", "a": "Activate the fire alarm immediately. Evacuate using stairs, not elevators. Stay low to avoid smoke. Close doors behind you to slow fire spread. Call 101 (Fire Services) once you are safe outside."},
        {"q": "How do I use a fire extinguisher?", "a": "Remember PASS: Pull the pin, Aim at the base of the fire, Squeeze the handle, Sweep side to side. Only use an extinguisher on small, contained fires. Evacuate if the fire is large."},
        {"q": "What should I do if my clothes catch fire?", "a": "Stop, Drop, and Roll. Stop immediately, drop to the ground, cover your face, and roll back and forth to smother the flames. Call for help and seek medical attention."},
        {"q": "How do I escape a smoke-filled room?", "a": "Crawl low under the smoke where air is cleaner. Feel doors before opening - if hot, do not open. Use a wet cloth over your nose and mouth. Signal from a window if you cannot escape."},
        {"q": "What is the fire emergency number?", "a": "Dial 101 for Fire Services or 112 for the National Emergency Number. Provide your exact location, nature of fire, and whether anyone is trapped."},
        {"q": "How do I prevent kitchen fires?", "a": "Never leave cooking unattended. Keep flammable materials away from the stove. Have a fire extinguisher in the kitchen. Install a smoke detector. Turn off gas after use."},
        {"q": "What should I do if I smell gas at home?", "a": "Do not switch on any lights or electrical appliances. Open all windows and doors. Turn off the gas supply at the meter. Evacuate immediately and call the gas emergency helpline or 112 from outside."},
        {"q": "How do I report a forest fire?", "a": "Call 1926 (Forest Fire Helpline) or 112. Provide the exact location, size of the fire, and direction it is spreading. Do not attempt to fight a forest fire yourself."},
        {"q": "What should I include in a home fire escape plan?", "a": "Identify two exits from every room. Designate a meeting point outside. Practice the plan with all family members. Ensure smoke detectors are working. Keep escape routes clear of obstacles."},
        {"q": "Are there fire safety rules for high-rise buildings?", "a": "Know the location of fire exits and extinguishers. Never block fire exits. Participate in fire drills. Do not use elevators during a fire. Report fire hazards to building management immediately."},
        {"q": "What causes most house fires?", "a": "Common causes include unattended cooking, faulty electrical wiring, candles left burning, overloaded power sockets, and improper storage of flammable materials."},
        {"q": "How do I treat a minor burn?", "a": "Cool the burn under cool (not cold) running water for at least 10 minutes. Do not apply ice, butter, or toothpaste. Cover with a clean, non-fluffy bandage. Seek medical help for severe burns."}
      ]
    },
    "earthquake": {
      "tag": "earthquake", "label": "Earthquake", "icon": "\U0001f3da\ufe0f",
      "faqs": [
        {"q": "What should I do during an earthquake?", "a": "Drop, Cover, and Hold On. Get under a sturdy table or desk, cover your head and neck, and hold on until shaking stops. Stay away from windows, heavy furniture, and exterior walls."},
        {"q": "What should I do after an earthquake?", "a": "Check for injuries and provide first aid. Inspect your home for damage. Watch for aftershocks. Do not use elevators. Avoid damaged buildings. Listen to official emergency broadcasts."},
        {"q": "Is it safe to go outside during an earthquake?", "a": "If indoors, stay indoors until shaking stops. If outdoors, move away from buildings, streetlights, and utility wires. Once shaking stops, look for a clear open area."},
        {"q": "What is the earthquake emergency number?", "a": "Call 112 (National Emergency) or the NDRF helpline at 011-24363260. Report injuries, trapped persons, or structural damage."},
        {"q": "How do I prepare an earthquake emergency kit?", "a": "Include water (3 litres/person/day for 3 days), non-perishable food, first aid kit, torch, batteries, whistle, dust mask, wrench to turn off utilities, and copies of important documents."},
        {"q": "What should I do if I am trapped under debris?", "a": "Do not light a match. Do not move unnecessarily to avoid disturbing debris. Cover your mouth with a cloth. Tap on a pipe or wall so rescuers can hear you. Use a whistle if available."},
        {"q": "How do I check if my building is safe after an earthquake?", "a": "Look for cracks in walls, ceilings, and foundations. Check for gas leaks (smell) and water leaks. Do not enter if you see major structural damage. Contact a structural engineer for assessment."},
        {"q": "What causes aftershocks?", "a": "Aftershocks are smaller earthquakes that follow the main quake as the earth crust adjusts. They can occur minutes, days, or weeks later. Treat each aftershock with the same Drop, Cover, Hold On response."},
        {"q": "How do I turn off utilities after an earthquake?", "a": "Turn off gas at the main valve if you smell gas. Turn off electricity at the main breaker if you see sparks or damaged wiring. Do not turn gas back on yourself - call the gas company."},
        {"q": "What should I do if a tsunami warning is issued after an earthquake?", "a": "Move immediately to higher ground or inland. Do not wait to see the wave. A tsunami can arrive within minutes of a coastal earthquake. Follow evacuation routes and official instructions."},
        {"q": "How do I help injured people after an earthquake?", "a": "Provide first aid for minor injuries. Do not move seriously injured people unless they are in immediate danger. Call 112 for medical assistance. Keep injured persons warm and calm."},
        {"q": "What are the earthquake risk zones in India?", "a": "India has 5 seismic zones (I to V). Zone V (highest risk) includes northeast India, parts of Jammu and Kashmir, Uttarakhand, and the Andaman and Nicobar Islands. Check your local zone with the NDMA."}
      ]
    },
    "cyclone": {
      "tag": "cyclone", "label": "Cyclone / Storm", "icon": "\U0001f300",
      "faqs": [
        {"q": "What should I do when a cyclone warning is issued?", "a": "Stay indoors and away from windows. Stock up on food, water, and medicines. Secure loose objects outside. Charge all devices. Follow official evacuation orders immediately if issued."},
        {"q": "What is the cyclone emergency helpline?", "a": "Call 1070 (National Disaster Helpline) or 112. For coastal areas, contact the Indian Meteorological Department (IMD) at 1800-180-1717 for weather updates."},
        {"q": "How do I prepare my home for a cyclone?", "a": "Reinforce doors and windows. Clear gutters and drains. Trim trees near your home. Store emergency supplies. Know your nearest cyclone shelter. Keep important documents in a waterproof bag."},
        {"q": "What should I do during the eye of a cyclone?", "a": "Do not go outside during the eye of the cyclone. The calm is temporary and dangerous winds will return from the opposite direction. Stay sheltered until authorities confirm the cyclone has passed."},
        {"q": "Where are cyclone shelters located?", "a": "Cyclone shelters are typically located at schools, community centres, and government buildings in coastal areas. Contact your local district administration or dial 1077 for the nearest shelter."},
        {"q": "What should I do after a cyclone passes?", "a": "Wait for official all-clear before going outside. Watch for downed power lines, flooding, and structural damage. Do not drink tap water until declared safe. Report damage to local authorities."},
        {"q": "How do I understand cyclone warning categories?", "a": "Category 1: Winds 90-125 km/h (minimal). Category 2: 125-164 km/h (moderate). Category 3: 165-224 km/h (extensive). Category 4: 225-279 km/h (extreme). Category 5: 280+ km/h (catastrophic). Evacuate for Category 3 and above."},
        {"q": "Is it safe to use a generator during a cyclone?", "a": "Never use a generator indoors or in an enclosed space - it produces deadly carbon monoxide. Use it only outdoors, away from windows and doors."},
        {"q": "How do I protect my livestock during a cyclone?", "a": "Move livestock to higher ground or sturdy shelters. Ensure they have food and water. Do not leave them tied in open areas. Contact your local animal husbandry department for assistance."},
        {"q": "What should fishermen do when a cyclone warning is issued?", "a": "Return to shore immediately. Do not venture into the sea. Secure boats at the harbour. Follow Coast Guard instructions. Dial 1554 (Coast Guard) for maritime emergencies."}
      ]
    },
    "medical": {
      "tag": "medical", "label": "Medical Emergency", "icon": "\U0001f691",
      "faqs": [
        {"q": "What is the medical emergency number?", "a": "Dial 108 for ambulance services or 112 for the National Emergency Number. Provide your exact location, the patient condition, and your contact number."},
        {"q": "What should I do if someone has a heart attack?", "a": "Call 108 immediately. Have the person sit or lie down comfortably. Loosen tight clothing. If trained, perform CPR if the person is unresponsive and not breathing. Do not give food or water."},
        {"q": "How do I perform CPR?", "a": "Check for responsiveness. Call 108. Place heel of hand on centre of chest. Push hard and fast (100-120 compressions/min, 5-6 cm deep). Give 2 rescue breaths after every 30 compressions if trained. Continue until help arrives."},
        {"q": "What should I do if someone is choking?", "a": "If they cannot speak or breathe, perform the Heimlich manoeuvre: stand behind them, make a fist above the navel, grasp with other hand, and give firm upward thrusts. Call 108 if unsuccessful."},
        {"q": "How do I treat a snake bite?", "a": "Keep the person calm and still. Immobilise the bitten limb below heart level. Remove jewellery near the bite. Do NOT cut, suck, or apply a tourniquet. Rush to the nearest hospital immediately. Call 108."},
        {"q": "What should I do if someone has a stroke?", "a": "Remember FAST: Face drooping, Arm weakness, Speech difficulty, Time to call 108. Note the time symptoms started. Do not give food, water, or medication. Keep the person calm and still."},
        {"q": "How do I treat severe bleeding?", "a": "Apply firm, direct pressure with a clean cloth. Do not remove the cloth if it soaks through - add more on top. Elevate the injured area above heart level if possible. Call 108 for severe bleeding."},
        {"q": "What should I do if someone is unconscious?", "a": "Check for breathing. Call 108. Place in recovery position (on their side) if breathing. Begin CPR if not breathing and you are trained. Do not give anything by mouth. Stay with them until help arrives."},
        {"q": "How do I handle a diabetic emergency?", "a": "If the person is conscious and can swallow, give sugar (juice, glucose tablets, or sugar water). If unconscious, do not give anything by mouth - call 108 immediately. Inform paramedics about the diabetes."},
        {"q": "What is the first aid for heat stroke?", "a": "Move the person to a cool, shaded area. Remove excess clothing. Cool them with wet cloths, ice packs on neck/armpits/groin, or a fan. Give cool water if conscious. Call 108 - heat stroke is life-threatening."},
        {"q": "How do I treat a fracture before the ambulance arrives?", "a": "Do not try to straighten the bone. Immobilise the injured area using a splint or padding. Apply ice wrapped in cloth to reduce swelling. Elevate if possible. Call 108 and keep the person still and calm."},
        {"q": "What should I include in a home first aid kit?", "a": "Bandages, sterile gauze, adhesive tape, antiseptic wipes, antiseptic cream, scissors, tweezers, thermometer, pain relievers, oral rehydration salts, gloves, and a first aid manual."}
      ]
    },
    "chemical": {
      "tag": "chemical", "label": "Chemical / Industrial Hazard", "icon": "\u2623\ufe0f",
      "faqs": [
        {"q": "What should I do if there is a chemical spill near my area?", "a": "Evacuate the area immediately upwind of the spill. Do not touch or inhale the substance. Call 112 and the local fire department (101). Follow official instructions and do not return until authorities declare it safe."},
        {"q": "What is the chemical emergency helpline?", "a": "Call 112 (National Emergency) or 1800-180-5999 (Chemical Emergency Helpline). For industrial accidents, contact the local factory inspectorate or district administration."},
        {"q": "How do I protect myself from chemical fumes?", "a": "Cover your nose and mouth with a wet cloth. Move upwind and to higher ground (many chemical gases are heavier than air). Seal windows and doors if sheltering indoors. Follow evacuation orders immediately."},
        {"q": "What should I do if I am exposed to a chemical substance?", "a": "Remove contaminated clothing. Flush skin and eyes with large amounts of clean water for at least 15-20 minutes. Do not induce vomiting if swallowed. Seek immediate medical attention and call 108."},
        {"q": "How do I identify a hazardous material vehicle?", "a": "Look for diamond-shaped HAZCHEM placards on vehicles with a number and colour code. Orange = explosive, Red = flammable, Yellow = oxidiser, White = corrosive, Green = non-flammable gas. Keep distance and call 112."},
        {"q": "What should I do during a gas leak in my building?", "a": "Do not operate electrical switches. Evacuate immediately. Do not use the elevator. Call the gas company emergency line and 101 from outside. Do not re-enter until authorities confirm it is safe."},
        {"q": "How do I shelter in place during a chemical emergency?", "a": "Go to an interior room above ground level. Close all windows, doors, and fireplace dampers. Turn off fans and air conditioning. Seal gaps with wet towels or tape. Monitor official broadcasts for further instructions."}
      ]
    },
    "general": {
      "tag": "general", "label": "General Emergency", "icon": "\U0001f198",
      "faqs": [
        {"q": "What are the key emergency numbers in India?", "a": "112: National Emergency (Police/Fire/Ambulance), 100: Police, 101: Fire, 108: Ambulance, 1077: State Disaster Helpline, 1070: National Disaster Helpline, 1554: Coast Guard, 1926: Forest Fire."},
        {"q": "What should every emergency kit contain?", "a": "Water (3L/person/day for 3 days), non-perishable food, first aid kit, torch with batteries, whistle, dust mask, plastic sheeting and duct tape, moist towelettes, garbage bags, wrench, manual can opener, local maps, and a battery-powered radio."},
        {"q": "How do I make an emergency plan for my family?", "a": "Identify local hazards. Know evacuation routes. Designate a meeting point. Share emergency contacts. Assign roles to family members. Practice the plan twice a year. Keep emergency kits ready."},
        {"q": "What is NDMA and how can it help?", "a": "The National Disaster Management Authority (NDMA) is India apex body for disaster management. Visit ndma.gov.in or call 1070 for guidelines, alerts, and assistance during national disasters."},
        {"q": "How do I report a missing person during a disaster?", "a": "Contact the local police (100), district administration, or the State Emergency Operations Centre. Provide a recent photo, physical description, last known location, and contact details."},
        {"q": "What should I do if there is a power outage during an emergency?", "a": "Use torches instead of candles to reduce fire risk. Keep refrigerator and freezer doors closed. Unplug sensitive electronics. Use generators only outdoors. Monitor battery-powered radio for updates."},
        {"q": "How do I stay informed during an emergency?", "a": "Monitor All India Radio (AIR), Doordarshan, and local TV/radio. Follow official social media accounts of NDMA, IMD, and local authorities. Download the Sachet app for disaster alerts. Avoid unverified social media rumours."},
        {"q": "What is the role of NDRF during disasters?", "a": "The National Disaster Response Force (NDRF) is a specialised force for disaster response. They conduct search and rescue, provide medical assistance, and support evacuation. Contact via 112 or local district administration."},
        {"q": "How do I help without putting myself at risk during a disaster?", "a": "Volunteer with registered organisations like Red Cross or local NGOs. Donate to verified relief funds. Share only verified information. Follow instructions from emergency personnel. Do not enter disaster zones without authorisation."},
        {"q": "What should I do if I witness an accident?", "a": "Ensure your own safety first. Call 112 immediately. Do not move injured persons unless in immediate danger. Provide basic first aid if trained. Keep the area clear for emergency vehicles. Stay until help arrives."},
        {"q": "How do I prepare children for emergencies?", "a": "Teach them emergency numbers. Practice evacuation drills. Use age-appropriate language to explain emergencies. Ensure they know their full name, address, and a parent phone number. Assign them simple roles in the family emergency plan."},
        {"q": "What mental health support is available after a disaster?", "a": "Contact iCall at 9152987821 or Vandrevala Foundation at 1860-2662-345 (24/7). NIMHANS offers disaster mental health support. Local health centres also provide counselling. It is normal to feel anxious - seek help without hesitation."}
      ]
    }
  }
}

with open("faq_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

total = sum(len(s["faqs"]) for s in data["scenarios"].values())
print(f"Scenarios: {len(data['scenarios'])} | Total FAQs: {total}")
