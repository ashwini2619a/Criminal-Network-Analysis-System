import { useState, useCallback } from 'react';
import * as api from '../lib/api';

export function useAnalysis() {
  const [centrality, setCentrality] = useState<any>(null);
  const [communities, setCommunities] = useState<any>(null);
  const [kingpins, setKingpins] = useState<any>(null);
  const [hawala, setHawala] = useState<any>(null);
  const [burnerPhones, setBurnerPhones] = useState<any>(null);
  const [loading, setLoading] = useState<Record<string, boolean>>({});

  const fetchAnalysis = useCallback(async (type: string, fetcher: () => Promise<any>, setter: (d: any) => void) => {
    setLoading(prev => ({ ...prev, [type]: true }));
    try {
      const data = await fetcher();
      setter(data);
    } catch (err) {
      console.error(`Error fetching ${type}:`, err);
    } finally {
      setLoading(prev => ({ ...prev, [type]: false }));
    }
  }, []);

  const fetchCentrality = () => fetchAnalysis('centrality', api.getCentrality, setCentrality);
  const fetchCommunities = () => fetchAnalysis('communities', api.getCommunities, setCommunities);
  const fetchKingpins = () => fetchAnalysis('kingpins', api.getKingpins, setKingpins);
  const fetchHawala = () => fetchAnalysis('hawala', api.getHawala, setHawala);
  const fetchBurnerPhones = () => fetchAnalysis('burnerPhones', api.getBurnerPhones, setBurnerPhones);

  const fetchAll = useCallback(() => {
    fetchCentrality();
    fetchCommunities();
    fetchKingpins();
    fetchHawala();
    fetchBurnerPhones();
  }, [fetchAnalysis]);

  return {
    centrality, communities, kingpins, hawala, burnerPhones,
    loading,
    fetchCentrality, fetchCommunities, fetchKingpins, fetchHawala, fetchBurnerPhones, fetchAll
  };
}
