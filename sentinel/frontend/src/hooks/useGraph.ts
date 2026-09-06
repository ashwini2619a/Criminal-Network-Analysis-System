import { useState, useCallback } from 'react';
import { GraphData, AnyNode, FilterState } from '../types';
import * as api from '../lib/api';

export function useGraph() {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<AnyNode | null>(null);
  const [filters, setFilters] = useState<FilterState>({ searchQuery: '', nodeTypes: [], minRiskScore: 0 });

  const fetchGraph = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getFullGraph();
      setGraphData(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch graph');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleExpandNode = useCallback(async (nodeId: string) => {
    try {
      return await api.expandNode(nodeId);
    } catch (err: any) {
      console.error(err);
      return null;
    }
  }, []);

  const search = useCallback(async (query: string) => {
    return api.searchNodes(query);
  }, []);

  const getPath = useCallback(async (src: string, tgt: string) => {
    return api.getShortestPath(src, tgt);
  }, []);

  return {
    graphData,
    loading,
    error,
    selectedNode,
    setSelectedNode,
    filters,
    setFilters,
    fetchGraph,
    handleExpandNode,
    search,
    getPath
  };
}
