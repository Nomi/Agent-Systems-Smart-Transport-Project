# Smart Transport Agent System - Technical Documentation

## Architecture Overview

This project implements a distributed multi-agent system using the SPADE (Smart Python Agent Development Environment) framework. The system simulates an intelligent transportation network through three types of cooperative agents communicating via XMPP protocol.

## Technology Stack

### Core Dependencies
- **SPADE Framework:** Agent platform built on XMPP for distributed agent communication
- **Python 3.x:** Primary programming language
- **asyncio:** Asynchronous programming for concurrent agent operations
- **colorama:** Terminal color output for visualization
- **numpy:** Array operations for map handling

### Communication Protocol
- **XMPP (Extensible Messaging and Presence Protocol):** Real-time messaging between agents
- **Jabber ID (JID):** Unique agent identification system
- **Message routing:** Asynchronous message passing with timeout handling

## System Components

### 1. CentralAgent (Central.py)

#### Class Structure
```python
class CentralAgent(Agent):
    timeOfStart: float
    passengers: dict  # JID -> passengerData mapping
    busses: dict     # JID -> busData mapping
    arrMap: list     # 2D grid representation
```

#### Core Responsibilities
- **Route Management:** Maintains a 2D grid map (`arrMap`) representing the transportation network
- **Agent Registry:** Tracks all active buses and passengers with their states
- **Assignment Algorithm:** Implements optimal bus-to-passenger matching based on:
  - Proximity calculation (Euclidean distance)
  - Bus availability and capacity
  - Passenger time constraints
  - Route compatibility

#### Message Protocol
**Incoming Messages:**
- `P:LOOKING_FOR_BUS:timeLimit:y:x` - Passenger ride request
- `P:GOT_ON_BUS` - Passenger boarding confirmation
- `P:FINISHED` - Passenger journey completion
- `B:MOVING:y:x:symbol:passengerCount:maxCapacity` - Bus location update
- `B:FULL_BUS:y:x:symbol:passengerCount:maxCapacity` - Full bus status
- `B:FINISHED` - Bus service completion

**Outgoing Messages:**
- `--[ACCEPT]--` / `--[REJECT]--` - Ride request responses
- `CEN:moveStatus:passengerStatus:y:x:passengerJID` - Bus coordination responses

#### Algorithm Details
```python
def assginBusToPassenger(self, hY:int, wX:int, timeLimit:int):
    # Finds optimal bus based on:
    # 1. Bus availability (!busyPickingPassenger)
    # 2. Capacity constraints (passengerCount != maxPassengers)
    # 3. Route compatibility (bus.pos.y±1 == passenger.y)
    # 4. Distance optimization (minimize wX - bus.pos.x)
    # 5. Time feasibility (distance < timeLimit)
```

### 2. BusAgent (Bus.py)

#### Finite State Machine Implementation
Uses SPADE's FSMBehaviour with four distinct states:

##### State Definitions
- **MOVING_STATE:** Normal route progression
- **PICKING_UP_CLIENT_STATE:** Passenger boarding process
- **FULL_BUSS_STATE:** At-capacity movement
- **FINAL_STOP_STATE:** Route termination

##### State Transitions
```python
# Valid transitions
MOVING → MOVING | PICKING_UP_CLIENT | FINAL_STOP
PICKING_UP_CLIENT → MOVING | FULL_BUSS
FULL_BUSS → FULL_BUSS | FINAL_STOP
FINAL_STOP → (terminal state)
```

#### Movement Algorithm
```python
async def run(self):  # Moving_StateBehavior
    # 1. Increment position: currentPos.x += 1
    # 2. Send location to CentralAgent
    # 3. Receive coordination response with timeout
    # 4. Process passenger pickup assignments
    # 5. Check collision avoidance (REJECT_MOVE handling)
    # 6. Maintain speed: sleep(TIME2SLEEP4 - processing_time)
```

#### Configuration Parameters
- `MAX_PASSENGERS`: Bus capacity limit
- `TIME2SLEEP4`: Movement speed (seconds per grid unit)
- `LAST_STOP`: Route termination point
- `SYMBOL_FULLBUSS` / `SYMBOL_NOTFULLBUSS`: Visual representation

### 3. PassengerAgent (Passenger.py)

#### State Machine Design
```python
LOOKING_FOR_RIDE → WAITING_FOR_RIDE → RIDING → FINISHED
                ↘                              ↗
                  FINISHED (timeout/rejection)
```

#### State Behaviors

##### LookForBus_StateBehavior
- Implements timeout-based ride request
- Handles accept/reject responses from CentralAgent
- Manages time limit enforcement

##### WaitingForBus_StateBehavior
- Waits for assigned bus arrival
- Processes `--[BUS_HERE]--` message
- Notifies CentralAgent of boarding

##### RidingBus_StateBehavior
- Monitors for destination arrival
- Processes `--[REACHED_DESTINATION]--` message
- Handles journey completion

#### Time Management
```python
timelimit = int(ARRMAP_WIDTH/2)  # Dynamic based on map size
searchTimeSoFar = int(time.time() - self.timeOfStart)
```

## Data Structures

### Helper Classes (AgentHelperFunctions.py)

#### passengerData
```python
class passengerData:
    pos: coordinates           # Current position
    assignedBusXmpp: Any      # Assigned bus JID
    gotOnBus: bool            # Boarding status
```

#### busData
```python
class busData:
    pos: coordinates          # Current position
    passengerCount: int       # Current load
    maxPassengers: int        # Capacity limit
    busyPickingPassenger: bool # Availability flag
```

#### coordinates
```python
class coordinates:
    x: int  # Grid width position
    y: int  # Grid height position
```

## Map System

### Grid Architecture
```python
def buildArrMap(height: int, width: int) -> list:
    # Creates 2D grid where:
    # - Every 3rd row (i+1)%3 == 0: roads ('=')
    # - Other rows: passenger areas (' ')
```

### Visualization System
- **Real-time rendering:** `printArrMapWithBounds(arrMap)`
- **Color coding:** Different agent types with colorama
- **Symbol mapping:**
  - `=`: Roads
  - `+`: Available bus
  - `>`: Full bus
  - `P`: Passenger (red if rejected)
  - `R`: Reserved passenger space

## Configuration System (config.py)

### Simulation Parameters
```python
# Agent Generation
NUM_PASSENGERS_TO_GENERATE: int = 6
NUM_BUSSES_TO_GENERATE: int = 4

# Map Configuration
ARRMAP_HEIGHT = 16
ARRMAP_WIDTH = 30
ENABLE_PASSENGER_SPACE_RESERVATION = True

# Bus Parameters
MAX_PASSENGERS = 2
TIME2SLEEP4 = 3  # seconds per movement
LAST_STOP = ARRMAP_WIDTH - 1

# XMPP Configuration
JID_BASE = "nomanspadehw@01337.io"
JID_PASSWORD = "lololol"
```

### Agent ID Management
```python
# ID allocation strategy
centralAgentJidAlias = 10
busJidAlias = 1000     # Range: 1000-1999
passJidAlias = 2000    # Range: 2000-2999
```

## Main Execution Flow (main.py)

### Initialization Sequence
1. **Central Agent Setup**
   ```python
   centralAg = CentralAgent(f"{JID_BASE}/{centralAgentJidAlias}", JID_PASSWORD)
   centralAg.start()
   ```

2. **Bus Fleet Deployment**
   ```python
   for i in range(NUM_BUSSES_TO_GENERATE):
       busAg = BusAgent(f"{JID_BASE}/{busJidAlias}", JID_PASSWORD)
       busAg.fillDetails(centralAgentAddress, 2+i*3, 0)  # Staggered positions
   ```

3. **Passenger Generation**
   ```python
   # Pre-create passenger agents
   # Spawn randomly during simulation
   # Dynamic rate: random.randint(0, 3) passengers per cycle
   ```

### Runtime Loop
```python
while centralAg.is_alive:
    # Dynamic passenger spawning
    # Random location assignment
    # Simulation timing control
    # Graceful shutdown handling
```

## Performance Considerations

### Scalability Factors
- **Message Volume:** O(n*m) where n=buses, m=passengers
- **Central Agent Load:** Single point of coordination
- **Memory Usage:** Linear with active agents
- **Network Latency:** XMPP overhead for local simulation

### Optimization Strategies
- **Batch Processing:** Multiple passenger requests per cycle
- **State Caching:** Avoid redundant map updates
- **Timeout Management:** Prevent deadlocks in async operations
- **Collision Avoidance:** Preemptive bus spacing

## Error Handling

### Exception Management
```python
try:
    # Agent operation
except:
    traceback.print_exc()  # Debug information
    # Graceful degradation
```

### Fault Tolerance
- **Message Loss:** Timeout-based retries
- **Agent Failure:** Isolation to prevent cascade
- **Network Issues:** Local XMPP resilience

## Development and Testing

### Code Organization
```
├── main.py                    # Entry point
├── config.py                  # Configuration parameters
├── helper.py                  # Utility functions
├── Agents/
│   ├── Central.py            # Central coordination agent
│   ├── Bus.py                # Bus fleet agents
│   ├── Passenger.py          # Passenger request agents
│   └── AgentHelperFunctions.py # Shared utilities
└── Trashbin/                 # Development artifacts
```

### Debugging Features
- **Colored Output:** Real-time state visualization
- **Message Tracing:** Communication flow debugging
- **State Logging:** Agent behavior monitoring
- **Map Visualization:** Spatial relationship display

## Deployment Requirements

### Runtime Dependencies
```bash
pip install spade colorama numpy
```

### XMPP Server Setup
- Local or remote XMPP server required
- Agent authentication configuration
- Message routing capabilities

### System Requirements
- Python 3.7+
- Asyncio support
- Terminal with color support (for visualization)

## Future Enhancements

### Potential Improvements
1. **Pathfinding:** A* algorithm for complex routes
2. **Load Balancing:** Dynamic bus redistribution
3. **Predictive Analytics:** Demand forecasting
4. **GUI Interface:** Web-based visualization
5. **Database Integration:** Persistent agent states
6. **Real-time Metrics:** Performance monitoring
7. **Multi-modal Transport:** Integration with other transport types

### Research Applications
- **Traffic Optimization:** Real-world traffic management
- **Resource Allocation:** General scheduling problems
- **Distributed Systems:** Consensus algorithms
- **AI Coordination:** Multi-agent reinforcement learning

---

**Technical Author:** Noman Noor  
**Framework:** SPADE (Smart Python Agent Development Environment)  
**Last Updated:** 2024

*For a non-technical overview, see [README.md](README.md)*

*For a non-technical overview, see [README.md](README.md)*