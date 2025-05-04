import React, { useState } from 'react';
import { provisionHub } from '../api/api';

export const HubProvisionForm: React.FC = () => {
  const [location, setLocation] = useState('');
  const [owner, setOwner] = useState('');
  const [workers, setWorkers] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await provisionHub({ location, owner, workers: workers.split(',') });
    alert('Hub provisioned successfully!');
    setLocation('');
    setOwner('');
    setWorkers('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <input placeholder="Location" value={location} onChange={e => setLocation(e.target.value)} />
      <input placeholder="Owner" value={owner} onChange={e => setOwner(e.target.value)} />
      <input placeholder="Workers (comma separated)" value={workers} onChange={e => setWorkers(e.target.value)} />
      <button type="submit">Provision Hub</button>
    </form>
  );
};
