export type ProductType = 'upper_garment' | 'laptop_bag'
export type StudioMode = 'local_private' | 'hybrid' | 'cloud_creative'

export interface Design {
  id: string
  name: string
  product_type: ProductType
  mode: StudioMode
  description: string
  measurements_mm: Record<string, number | null>
  materials: string[]
  components: string[]
  revision: number
  approval_state: string
  confidence: string
  missing: string[]
  created_at: string
  updated_at: string
}

export interface Brief {
  product_type: ProductType
  confirmed: {
    components?: string[]
    materials?: string[]
    measurements_mm?: Record<string, number>
  }
  estimated: Record<string, unknown>
  missing: string[]
  next_question: string | null
}

export interface RagResult {
  title: string
  source: string
  excerpt: string
  score: number
  source_page?: number | null
  chunk_number?: number | null
  chunk_id?: string | null
}

export interface Job {
  id: string
  kind: string
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'
  gpu_exclusive: boolean
  payload: Record<string, unknown>
  progress: number
  total: number | null
  message: string | null
  error: string | null
  created_at: string
  updated_at: string
}

export interface AssistantReply {
  message: string
  actions: string[]
  design: Design
}
