import { useQuery, useMutation } from 'react-query'
import api from '../services/api'
import type {
  VerificationResponse,
  IntegrityReport,
  MerkleProof,
} from '../types'

interface VerifyParams {
  decision_id?: string
  audit_log_id?: string
  merkle_root?: string
  start_date?: string
  end_date?: string
  organization_id?: string
}

export function useVerification(params: VerifyParams) {
  return useMutation<VerificationResponse>(
    async () => {
      const { data } = await api.post('/verify/', params)
      return data
    }
  )
}

export function useIntegrityReport(
  organizationId: string,
  startDate?: string,
  endDate?: string
) {
  return useQuery<IntegrityReport>(
    ['integrity-report', organizationId, startDate, endDate],
    async () => {
      const params: Record<string, string> = {}
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate

      const { data } = await api.get(`/verify/integrity-report/${organizationId}`, {
        params,
      })
      return data
    },
    {
      enabled: !!organizationId,
    }
  )
}

export function useMerkleProof(decisionId: string) {
  return useQuery<MerkleProof>(
    ['merkle-proof', decisionId],
    async () => {
      const { data } = await api.get(`/verify/merkle-proof/${decisionId}`)
      return data
    },
    {
      enabled: !!decisionId,
    }
  )
}

export function useVerifyMerkleProof() {
  return useMutation<
    { verified: boolean; leaf_hash: string; root_hash: string; timestamp: string },
    unknown,
    { leaf_hash: string; root_hash: string; proof_path: Array<{ hash: string; position: 'left' | 'right' }> }
  >(
    async (proofData) => {
      const { data } = await api.post('/verify/merkle', null, {
        params: proofData,
      })
      return data
    }
  )
}

export function useHashDetails(decisionId: string) {
  return useQuery(
    ['hash-details', decisionId],
    async () => {
      const { data } = await api.get(`/verify/hash/${decisionId}`)
      return data
    },
    {
      enabled: !!decisionId,
    }
  )
}
