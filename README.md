# Smart Transport Agent System

A multi-agent simulation system that models intelligent public transportation using autonomous software agents.

## What This Project Does

This project simulates a smart city transportation system where buses, passengers, and a central dispatch system work together autonomously to provide efficient public transit. Think of it as a digital twin of a bus system where each component can think and make decisions on its own.

### The Big Picture

Imagine a city where:
- Buses drive themselves and know where to pick up passengers
- Passengers can request rides and get matched with the best available bus
- A central system coordinates everything to avoid conflicts and optimize routes
- All of this happens automatically without human intervention

This simulation demonstrates how autonomous agents (computer programs that can make decisions) can work together to solve complex transportation problems.

## How It Works

### The Three Types of "Smart Agents"

#### 1. The Central Coordinator (CentralAgent)
**What it does:** Acts like a smart traffic control center that can see everything happening in the city.

**How it behaves:**
- Maintains a real-time map of where all buses and passengers are located
- When a passenger requests a ride, it finds the best bus to send
- Prevents buses from crashing into each other by managing traffic
- Keeps track of which passengers are on which buses
- Makes decisions about the most efficient way to serve everyone

**Think of it as:** A very smart dispatcher who never sleeps and can instantly see the entire city.

#### 2. The Smart Buses (BusAgent)
**What they do:** Self-driving buses that can think about their routes and passenger service.

**How they behave:**
- **Moving State:** Drive along their route, checking for passengers to pick up
- **Picking Up State:** Stop when they find a passenger and let them board
- **Full Bus State:** When at capacity, continue to the end without picking up more passengers
- **Final Stop State:** Arrive at destination and let everyone off

**Key characteristics:**
- Each bus has a maximum passenger capacity (configurable)
- They communicate their location to the central coordinator constantly
- They can identify when they need to pick up specific passengers
- They follow traffic rules to avoid collisions

**Think of them as:** Autonomous buses with their own "brain" that can make decisions about picking up passengers.

#### 3. The Smart Passengers (PassengerAgent)
**What they do:** Represent people who need transportation and can interact with the system.

**How they behave:**
- **Looking for Ride:** Request a bus from the central system with a time limit
- **Waiting for Ride:** Wait at their location for the assigned bus to arrive
- **Riding:** Travel on the bus to their destination
- **Finished:** Complete their journey successfully or give up if no bus comes

**Key characteristics:**
- Each passenger has a time limit for how long they'll wait for a bus
- They appear randomly at different locations in the city
- They communicate with both the central system and buses
- They can "give up" if service takes too long

**Think of them as:** Smart phone apps that can automatically request and coordinate rides.

### The City Map

The simulation uses a grid-based city layout:
- **Roads** are represented by horizontal lines (=) where buses travel
- **Passenger areas** are spaces above and below roads where people wait
- **Coordinates** track exact positions of all agents
- **Real-time visualization** shows the current state of the entire system

### Communication and Coordination

All agents communicate through messages, similar to how people might text or call each other:

- **Passengers → Central:** "I need a ride from location X with a Y-minute time limit"
- **Central → Passenger:** "Bus accepted/rejected your request"
- **Buses → Central:** "I'm at location X with Y passengers"
- **Central → Bus:** "Pick up passenger at location Z"
- **Bus → Passenger:** "I'm here to pick you up"
- **Bus → Passenger:** "We've reached your destination"

### What Makes It "Smart"

1. **Autonomous Decision Making:** Each agent can think and act independently
2. **Real-time Adaptation:** The system responds to changing conditions instantly
3. **Efficient Resource Allocation:** Buses are assigned optimally based on distance and availability
4. **Conflict Resolution:** The central system prevents buses from colliding
5. **Time Management:** Passengers have realistic expectations about wait times
6. **Scalability:** Can handle multiple buses and passengers simultaneously

## Why This Matters

This simulation demonstrates concepts used in:
- **Smart Cities:** How autonomous systems can manage urban transportation
- **Multi-Agent Systems:** How independent software agents can collaborate
- **Artificial Intelligence:** How computers can make intelligent decisions
- **Real-time Systems:** How to coordinate multiple moving parts instantly
- **Resource Optimization:** How to efficiently allocate limited resources (buses) to meet demand (passengers)

## Configuration and Customization

The system is highly configurable:
- **Number of buses and passengers** can be adjusted
- **Map size** can be changed to simulate different city sizes
- **Bus capacity** and **passenger time limits** are customizable
- **Movement speed** and **timing** can be modified
- **Visualization options** can be enabled or disabled

## Running the Simulation

When you run the simulation, you'll see:
1. A text-based map showing the city layout
2. Buses (represented by + or >) moving along roads
3. Passengers (P) appearing at various locations
4. Real-time updates as agents interact
5. Colored output showing different types of events
6. Statistics about successful and failed journeys

The simulation continues until all passengers have been served or have given up, demonstrating how the system handles varying demand and resource constraints.

---

**Author:** Noman Noor

*For technical implementation details, see [README-technical.md](README-technical.md)*

---

**Disclaimer:** This documentation was generated with AI assistance.
