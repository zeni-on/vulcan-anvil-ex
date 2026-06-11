export const DOC_COMMENT_CATEGORIES = [
  'note',
  'question',
  'finding-candidate',
  'cr-candidate',
  'issue-candidate',
  'typo',
] as const

export const DOC_COMMENT_STATUSES = [
  'open',
  'closed',
] as const

export type DocCommentCategory = (typeof DOC_COMMENT_CATEGORIES)[number]
export type DocCommentStatus = (typeof DOC_COMMENT_STATUSES)[number]

export interface DocCommentAnchor {
  type: 'line_range'
  start_line: number
  end_line: number
  selected_text: string
  heading?: string
}

export interface DocComment {
  comment_id: string
  document: string
  anchor: DocCommentAnchor
  category: DocCommentCategory
  body: string
  status: DocCommentStatus
  created_by: 'user' | 'agent'
  created_at: string
  updated_at: string
}

export interface DocCommentDraftAnchor {
  start_line: number
  end_line: number
  selected_text: string
  heading?: string
}

export interface DocCommentsResponse {
  comments: DocComment[]
  fetchedAt: string
}
