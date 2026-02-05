import { useQuery, useMutation, useQueryClient } from 'react-query'
import api from '../services/api'
import type { AuditLog, AuditStats, DecisionLineage } from '../types'

interface ListParams {
  organization_id: string
  page?: number
  page_size?: number
  start_date?: string
  end_date?: string
  include_deleted?: boolean
}

interface ListResponse {
  items: AuditLog[]
  total: number
  page: number
  page_size: number
  pages: number
}

export function useAuditLogs(params: ListParams) {
  return useQuery<ListResponse>(
    ['audit-logs', params],
    async () => {
      const { data } = await api.get('/audit/logs', { params })
      return data
    },
    {
      keepPreviousData: true,
    }
  )
}

export function useAuditLog(decisionId: string, includeDeleted = false) {
  return useQuery<AuditLog>(
    ['audit-log', decisionId],
    async () => {
      const { data } = await api.get(`/audit/logs/${decisionId}`, {
        params: { include_deleted: includeDeleted },
      })
      return data
    },
    {
      enabled: !!decisionId,
    }
  )
}

export function useDecisionLineage(decisionId: string) {
  return useQuery<DecisionLineage>(
    ['decision-lineage', decisionId],
    async () => {
      const { data } = await api.get(`/audit/lineage/${decisionId}`)
      return data
    },
    {
      enabled: !!decisionId,
    }
  )
}

export function useAuditStats(organizationId: string) {
  return useQuery<AuditStats>(
    ['audit-stats', organizationId],
    async () => {
      const { data } = await api.get(`/audit/stats/${organizationId}`)
      return data
    },
    {
      enabled: !!organizationId,
    }
  )
}

export function useCreateAuditLog() {
  const queryClient = useQueryClient()

  return useMutation(
    async (logData: unknown) => {
      const { data } = await api.post('/audit/logs', logData)
      return data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('audit-logs')
      },
    }
  )
}
