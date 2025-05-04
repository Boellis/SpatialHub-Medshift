export interface SensorData {
    id: number;
    hub_id: string;
    sensor_name: string;
    device_addr: string;
    sensor_val: number;
    datetime: string;
    sensor_id: string;
    location?: string;
    owner?: string;
    workers?: string[];
  }
  