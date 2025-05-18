# 🌊 Port Operations Simulation with Dash

## 📋 Overview
An advanced, interactive port operations simulator built with Python, Dash, and Plotly. This comprehensive simulation models complex port logistics with realistic ship movements, dynamic weather conditions, and detailed financial tracking. The application provides real-time visualization of port operations, queue dynamics, and economic performance metrics.

## 🚢 Key Features

### 1. Ship Management System
- **Three Ship Classes**:
  - **Small**: 500 containers (default), Priority 1
  - **Medium**: 2,000 containers (default), Priority 2
  - **Large**: 5,000 containers (default), Priority 3
- **Dynamic Distribution Control**:
  - Adjustable percentage sliders for each ship class (0-100%)
  - Real-time validation ensuring total distribution equals 100%
- **Priority-Based Processing**:
  - Optional priority queuing (Large > Medium > Small)
  - Visual indicators for ship priority in the queue

### 2. Port Operations
- **Berth Management**:
  - Configurable number of berths (1-60)
  - Real-time visual occupancy status
  - Berth productivity tracking (1-100,000 containers/hour)
- **Cargo Handling Process**:
  1. **Pilotage Phase** (1-240 minutes)
  2. **Mooring/Unmooring** (1-60 minutes)
  3. **Cargo Operations** (dynamically calculated based on container count and berth productivity)
- **Dynamic Weather System**:
  - Configurable bad weather probability (0-100%)
  - Adjustable weather duration (10-600 minutes)
  - 50% productivity reduction during bad weather
  - Visual weather indicators and warnings

### 3. Economic Simulation
- **Revenue Tracking**:
  - Configurable income per container ($0.10-$1,000)
  - Real-time revenue calculation and visualization
- **Cost Structure**:
  - Variable costs per container ($0-$1,000)
  - Monthly maintenance costs (up to $1,000,000)
  - Hourly maintenance cost allocation
- **Financial Analytics**:
  - Real-time profit/loss calculation
  - Profit margin percentage
  - Historical financial performance tracking

## 🛠️ Technical Implementation

### Simulation Core
- **Time-based Simulation**:
  - Minute-by-minute operation tracking
  - Configurable simulation speed (1x to 10x real-time)
- **State Management**:
  - Centralized state using Dash Store
  - Persistent simulation state across callbacks
- **Visualization Engine**:
  - Interactive Plotly graphs
  - Real-time updates
  - Responsive design

![](/images/animation.gif)

### Mathematical Models

#### 1. Ship Arrival Process
- **Poisson Process**:
  - Configurable arrival rate (λ = ships/hour)
  - Inter-arrival times: Exponential distribution f(t) = λe^(-λt)
  - Random ship class assignment based on distribution

#### 2. Service Time Calculation
```
Total Service Time = (Number of Containers / Berth Productivity) + 
                   Pilotage Time + 
                   Mooring/Unmooring Time
```
- **Container Processing**:
  - Continuous processing during service time
  - Real-time income/cost calculation

#### 3. Queue Management
- **Queue Discipline**:
  - First-Come-First-Served (default)
  - Optional Priority-based (Large > Medium > Small)
- **Queue Visualization**:
  - Automatic multi-row layout for large queues
  - Visual ship class indicators

#### 4. Weather System
- **Weather Events**:
  - Random occurrence based on probability
  - Duration: Uniform distribution between configurable bounds
- **Operational Impact**:
  - Complete halt of all port operations
  - No ship movements or cargo operations during bad weather
  - Visual weather warnings

![](/images/weather.gif)

#### 5. Financial Model
```
Income = Σ(Containers Handled × Income per Container)
Costs = (Σ(Containers Handled × Cost per Container)) + 
        (Monthly Maintenance Cost / 43,200)  # 30 days in minutes
Profit = Income - Costs
Profit Margin = (Profit / Income) × 100%
```

## ⚙️ Configuration Parameters

![](/images/parameters.png)

### 1. Ship Configuration
| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| Arrival Rate | 1-100 ships/hour | 20 | Average ships arriving per hour |
| Small Ship Containers | 1-1,000 | 500 | Container capacity for small ships |
| Medium Ship Containers | 1-2,000 | 2,000 | Container capacity for medium ships |
| Large Ship Containers | 1-30,000 | 5,000 | Container capacity for large ships |
| Ship Distribution | 0-100% each | 50/30/20 | Percentage distribution among ship classes |

### 2. Port Operations
| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| Number of Berths | 1-60 | 3 | Available berths in the port |
| Berth Productivity | 1-100,000 | 3,000 | Containers processed per hour |
| Pilotage Time | 1-240 min | 30 | Time to guide ship to berth |
| Mooring/Unmooring Time | 1-60 min | 5 | Time to secure/release ship |

### 3. Economic Parameters
| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| Income per Container | $0-$1,000 | $10.00 | Revenue per container handled |
| Cost per Container | $0-$1,000 | $2.00 | Cost per container handled |
| Monthly Maintenance | $0-$1,000,000 | $50,000 | Fixed monthly operating costs |

### 4. Weather Settings
| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| Bad Weather Probability | 0-100% | 10% | Chance of bad weather occurring |
| Weather Duration | 10-600 min | 10-50 | Range of possible weather durations |

### 5. Simulation Control
| Parameter | Options | Default | Description |
|-----------|---------|---------|-------------|
| Simulation Speed | 1x to 10x | 1x | Speed multiplier for simulation |
| Priority Handling | Toggle | On | Enable/disable priority queuing |

## 📊 Performance Metrics

### Real-time Monitoring
- **Queue Statistics**:
  - Current queue length
  - Maximum queue length
  - Average waiting time
  - Ship processing rate

- **Berth Utilization**:
  - Current utilization percentage
  - Average utilization over time
  - Berth occupancy status

- **Financial Metrics**:
  - Total income
  - Operating costs
  - Profit/Loss
  - Profit margin

### Simulation Results
After 500 minutes (8h 20m) of simulation time, a detailed report is generated including:
- Queue statistics
- Berth utilization
- Financial summary
- Performance metrics

![](/images/results.png)

## 📦 Dependencies

- **Core**:
  - Python 3.7+
  - Dash 2.0+
  - Plotly 5.0+
  - Pandas 1.0+

## 🙏 Special Thanks

I would like to express my deepest gratitude to my best friend, a professional Merchant Navy Navigator, for his invaluable consultations and expert guidance throughout the development of this project. His real-world experience and insights into port operations and maritime logistics were instrumental in making this simulation as accurate and realistic as possible.
