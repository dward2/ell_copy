import json
import logging
import numpy as np
import os


class Patient:
    RHO = 1.199  # kg/m3
    D1, D2 = 0.015, 0.012  # meters
    A1 = np.pi * (D1 / 2)**2
    A2 = np.pi * (D2 / 2)**2
    '''
    Represents patient CPAP data and parses through it.
    '''

    def __init__(self, filename):
        '''
        Initializes the patient object, parses through the data file.

        Args:
            filename(str): The path to the input file
            times, flows, metrics
        '''
        self.filename = filename
        self.output_name = filename.split('.')[0] + ".json"
        self.times = []
        self.flows = []
        self.v1_p2_adc = []
        self.v1_p1_ins_adc = []
        self.v1_p1_exp_adc = []
        self.metrics = {}
        self.parse_data()

    def parse_data(self):
        '''
        Processes the patient data file.
        Opens the file, skips header line and iterates through the points.
        Valid data is put into its respective variables.
        Invalid rows are logged as errors and skipped.
        '''
        logging.info(f"Starting data analysis for input file: {self.filename}")
        try:
            with open(self.filename, 'r') as file:
                next(file)
                for line_num, line in enumerate(file, 2):
                    try:
                        data = self.parse_line(line)
                        self.times.append(data[0])
                        self.v1_p2_adc.append(data[1])
                        self.v1_p1_ins_adc.append(data[2])
                        self.v1_p1_exp_adc.append(data[3])
                    except ValueError as error:
                        logging.error(
                            f"Line {line_num}: Incorrect data ({error}). "
                            "Skipping."
                        )
                        continue
        except FileNotFoundError:
            logging.error(f"File {self.filename} not found.")
            return
        self.pressures_p2 = self.pressure_conversion(
            self.v1_p2_adc
        )
        self.pressures_p1_ins = self.pressure_conversion(
            self.v1_p1_ins_adc
        )
        self.pressures_p1_exp = self.pressure_conversion(
            self.v1_p1_exp_adc
        )
        self.flows = self.flow_calculation(
            self.pressures_p2,
            self.pressures_p1_ins,
            self.pressures_p1_exp
        )

    def parse_line(self, line):
        '''
        Parses and validates a single comma-separated string of sensor data.
        Strips whitespace and splits the strin into parts.
        Converts each value to a float and checks for NaN values.
        Checks that the row has the correct amount of column data (7).

        Args:
            line (str): A raw string from the
            input file containing CPAP data.
        Returns:
            list of float: A list containing
            exactly 7 validated numeric values.
        Raises:
            ValueError:
            If the line has <7 columns or
            contains 'NaN'
        '''
        parts = line.strip().split(',')

        if len(parts) < 7:
            raise ValueError("Missing columns")

        data = []
        for x in parts:
            value = float(x)
            if np.isnan(value):
                raise ValueError("Contains NaN")
            data.append(value)

        return data

    def pressure_conversion(self, adc_list):
        '''Converts raw ADC integer values
        into pressure readings in cm-H2O.
        Uses the ADC specification formula:
        Pressure =
        [(25.4) / (14745 - 1638)] * (ADC_value - 1638).
        Args:
            adc_list (list of int):
            A list of raw integer values from the
                analog-to-digital converter.
        Returns:
            list of float:
            A list of converted values in cm-H2O.
        '''
        s = 25.4 / (14745 - 1638)
        return [s * (adc - 1638) for adc in adc_list]

    def flow_calculation(self, p2_list, p1_ins_list, p1_exp_list):
        '''Calculates volumetric
        flow rates using Bernoulli's principle for Venturi tubes.
        Determines flow direction
        by comparing inspiration and expiration pressures.
        Converts pressure differential to Pascals.
        Calculates velocity to find
        the flow rate in Liters per second (L/s).

        Args:
        p2_list (list of float):
            Pressures at the tube constriction (cm-H2O).
        p1_ins_list (list of float):
            Upstream inspiration pressures (cm-H2O).
        p1_exp_list (list of float):
            Upstream expiration pressures (cm-H2O).

        Returns:
            list of float:
            Volumetric flow rates in Liters per second (L/s)
        '''
        calculated_flow = []
        area_ratio_sq = (self.A2 / self.A1)**2
        d = self.RHO * (1 - area_ratio_sq)
        for p2, p1_ins, p1_exp in zip(p2_list, p1_ins_list, p1_exp_list):
            if p1_ins >= p1_exp:
                p1_active = p1_ins
                direction = 1
            else:
                p1_active = p1_exp
                direction = -1

            con_pascals = abs(p1_active - p2) * 98.0665
            velocity = np.sqrt((2 * con_pascals) / d)
            flow = (self.A2 * velocity) * 1000 * direction
            calculated_flow.append(flow)
        return calculated_flow

    def metrics_calculation(self):
        '''
        Analyzes flow data to calculate clinical respiratory metrics.
        Calculates total duration,
        Total mask leakage (volume),
        Breath cout via peak detection,
        average breath rate, and
        the number of apnea events.
        Creates:
             'metrics' dictionary with the values.
        Raises:
            Warning:
            If the calculated total leakage volume is negative.

        '''
        duration = self.times[-1] - self.times[0]
        total_leakage = 0
        for i in range(len(self.flows) - 1):
            time_step = self.times[i+1] - self.times[i]
            total_leakage += self.flows[i] * time_step
        if total_leakage < 0:
            logging.warning(f"Leakage is negative: {total_leakage}")

        threshold = 0.2
        min_gap = 1.5
        last_breath_time = -min_gap
        breath_times = []
        n = len(self.flows)
        for i in range(1, n - 1):
            current_f = self.flows[i]
            current_t = self.times[i]

            if current_f > threshold:
                if current_f > self.flows[i-1] and current_f > self.flows[i+1]:
                    if current_t - last_breath_time >= min_gap:
                        breath_times.append(float(current_t))
                        last_breath_time = current_t

        apnea_count = 0
        for i in range(1, len(breath_times)):
            if (breath_times[i] - breath_times[i-1]) > 10.0:
                apnea_count += 1

        duration_minutes = duration / 60.0
        if duration_minutes > 0:
            breath_rate = len(breath_times) / duration_minutes
        else:
            breath_rate = 0.0

        self.metrics = {
            "duration": float(duration),
            "breaths": int(len(breath_times)),
            "breath_rate_bpm": float(breath_rate),
            "breath_times": breath_times,
            "apnea_count": int(apnea_count),
            "leakage": float(total_leakage)
        }

    def create_json(self):
        '''Saves the calculated metrics into a JSON file.
        Extracts the name form the input file, changes the
        extention from .txt to json.
        Raises:
            IOError: if the system is unable to write the file

        '''
        filename = os.path.basename(self.filename)
        name = os.path.splitext(filename)[0]
        json_filename = f"{name}.json"
        try:
            with open(json_filename, 'w') as f:
                json.dump(self.metrics, f, indent=4)
            logging.info(f"Successfully saved metrics to {json_filename}")
        except IOError as e:
            logging.error(f"Could not save JSON file {json_filename}: {e}")


def cpap_analysis(filename):
    """Analyze CPAP data file and return results for GUI display.

    Args:
        filename (str): path to the CPAP data file.

    Returns:
        dict: containing breathing_rate, apnea_count,
              flow_data, and time_data.
    """
    patient = Patient(filename)
    patient.metrics_calculation()

    results = {
        "breathing_rate": patient.metrics["breath_rate_bpm"],
        "apnea_count": patient.metrics["apnea_count"],
        "flow_data": patient.flows,
        "time_data": patient.times
    }
    return results


if __name__ == "__main__":
    logging.basicConfig(filename="log.txt", filemode="w", level=logging.INFO)
    filename = "sample_data/patient_08.txt"
    results = cpap_analysis(filename)
    print(results)
