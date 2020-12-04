# Technical Institute of Fire Protection in Prague (TIFP)

### Experimental Conditions: TGA, DSC
TGA and DSC were performed simultaneously using an STA apparatus.
STA experiments performed both in nitrogen and in air. Although tests were conducted simultaneously, TGA and DSC measurement data presented here are separated into two files, for consistency with other datasets.
Note: DSC heat flow data was rescaled (multiplied by -1)such that endothermic heat flow events are positive (endo up)

##### STA Tests in Nitrogen
* Heating Rate: 10 K/min
* Temperature program
  - Initial Temperature: 300.15 K
  - Initial Isotherm: 5 minutes
  - Maximum Temperature: 823.15 K
  - Final Isotherm: None
* Sample mass: ~5.4 mg
* Sample geometry: powdered
* Calibration type: nitrogen 70 ml/min, Al2O3 crucible, open, 10 °C/min, 20 to 1000 °C, material In, Bi, Zn, Al, Ag
* Crucible
  - Type: Al2O3
  - Volume: 85 µL
  - Diameter: None
  - Mass: None
  - Lid: False
  - Note: None
* Carrier Gas
  - Type: Nitrogen
  - Flow rate: 70 ml/min
  - Note: Pure Nitrogen (0% O2), purge flow 50 ml/min + protective 20 ml/min
* Instrument
  - Type: STA apparatus
  - Note: Simultaneous Thermal Analysis (TGA + DSC), measurement data presented as two separated files

###### Test Condition Summary

| Test Label | Heating Rate [K/min] | Initial Sample Mass [mg] | Oxygen Concentration [vol %] |
|:----------:|:--------------------:|:------------------------:|:------------------------------:|
| TIFP\_STA\_N2\_10K\_1 | 10 | 5.4338| 0 |  
| TIFP\_STA\_N2\_10K\_2 | 10 | 5.3668| 0 |  

### Experimental Conditions: STA
The above heading is here to divide the README file for when it is automatically processed until we have decided on a way to deal with the different experimental conditions for the automatic processing.

##### STA Tests in Air
* Heating Rate: 10 K/min
* Temperature program
  - Initial temperature 298.15 K
  - Isotherm: None
  - Maximum Temperature 1023.15 K
* Sample mass: ~5.85 mg
* Sample geometry: powdered
* Calibration type: air,  10 °C/min, material In
* Crucible type: Al2O3, 70 microliters, no lid
* Carrier Gas
  - Air (vol. % O2 = ambient)
  - Flow rate = purge flow 50 ml/min + protective 10 ml/min

###### Test Condition Summary

| Test Label | Heating Rate [K/min] | Initial Sample Mass [mg] | Oxygen Concentration [vol. %] |
|:----------:|:--------------------:|:------------------------:|:------------------------------:|
| TIFP\_STA\_O2-21\_10K\_1 | 10 | 4.4790 | 21 (Ambient) |  
| TIFP\_STA\_O2-21\_10K\_2 | 10 | 5.2040 | 21 (Ambient) |  



### Experimental Conditions: Cone Calorimeter
Three runs were performed for each heat flux. Backside temperature measured by K type thermocouples glued to the sample in the middle (x=0, y=0) and at location x=-25 mm, y=0.

Note: For consistency with datasets submitted by other institutions, cone calorimeter HRR measurements submitted by TIFP have been normalized by sample surface area (nominal) to provide HRR per unit area [kW/m2]


* Heat Flux: 25 and 65 kW/m²
* Sample
  - Material: Black PMMA
  - Mass: None g [?]
  - Shape: square
  - Diameter or edge length: None m
  - Exposed surface area (nominal): 0.0084 m²
  - Thickness: None m
  - Note: None
* Sample holder
  - Shape: square
  - Retainer frame: True
  - Retaining grid: False
  - Note: according to ISO 5660-1, stainless steel
* Sample chamber
  - Top opening: None
  - Doors/Windshield: None
  - Bottom opening: None
  - Note: None
* Backing
  - Material 1: Earth-alkali silicate wool
  - Thickness 1: None m [?]
  - Density 1: None kg/m³ [?]
  - Conductivity 1: 0.16 W/(m K) @ 600K
  - Specific heat capacity 1: None J/(kg K) [?]
  - Note 1: None
* Thermocouple
  - Type 1: K type
  - Location 1: x=0.0 m, y=0.0 m, z=0.0 m
  - Surface 1: Back
  - Note 1: glued to back surface of sample, at center
  - Type 2: K type
  - Location 2: x=-0.025 m, y=0.0 m, z=0.0 m
  - Surface 2: Back
  - Note 2: Glued to the sample
* Carrier gas
  - Type: Air [?]
  - Flow rate: 24 l/s
  - Note: None
* Calibration
  - Type: None [?]
  - Frequency: None [?]
  - Note: None
* Instrument
  - Manufacturer: None [?]
  - Apparatus and model number: None [?]
  - Note: None

###### Test Condition Summary

| Test Label | Initial Sample Mass (g) | Heat Flux (kW/m²) | Avg. Heater Temperature (K) | Time to Ignition (s) |
|:------:|:------:|:------:|:------:|:------:|
| TIFP_Cone_25kW_1 | None [?] | 25 | 1134.65 | None [?] |
| TIFP_Cone_25kW_2 | None [?] | 25 | 1134.65 | None [?] |
| TIFP_Cone_25kW_3 | None [?] | 25 | 1134.65 | None [?] |
| TIFP_Cone_65kW_1 | None [?] | 65 | 1397.15 | None [?] |
| TIFP_Cone_65kW_2 | None [?] | 65 | 1397.15 | None [?] |
| TIFP_Cone_65kW_3 | None [?] | 65 | 1397.15 | None [?] |



### Experimental Conditions: Gasification Test

* Radiant heat flux 65 kW/m2, two runs were performed in a cone calorimeter apparatus with vitiated atmosphere module, pure nitrogen.
* Extraction flow rate: 24L/s
* Sample Surface Area: 0.0084 m2
* Sample holder dimensions
  - according to ISO 5660-1, stainless steel
  - Retainer frame/grid: frame was used
* Backing Insulation: earth-alkali silicate wool, [thickness?], thermal conductivity at 600K 0.16 kW/m/K
* Thermocouple location: None

###### Test Condition Summary

| Test Name | Heat Flux (kW/m2) | Heater Temperature (K) |
|:----------:|:------:|:---:|
| TIFP_Gasification_65kW_1 | 65 | 1403.15 |
| TIFP_Gasification_65kW_2 | 65 | 1403.15 |
