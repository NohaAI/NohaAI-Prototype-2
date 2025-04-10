'use client'

import { useState } from 'react'

export default function Dialog() {
    const [open, setOpen] = useState(true)

    return (
        <>
            <button className="btn btn-primary" data-modal-toggle="#modal_1">
                Show Modal
            </button>
            <div className="modal" data-modal="true" id="modal_1">
                <div className="modal-content max-w-[600px] top-[20%]">
                    <div className="modal-header">
                        <h3 className="modal-title">
                            Modal Title
                        </h3>
                        <button className="btn btn-xs btn-icon btn-light" data-modal-dismiss="true">
                            <i className="ki-outline ki-cross">
                            </i>
                        </button>
                    </div>
                    <div className="modal-body">
                        Modal components are commonly used for various purposes such as displaying login forms, confirming actions, presenting multimedia content, or showing detailed information.
                        They provide a non-intrusive way to engage users and guide them through specific tasks or actions while maintaining the context of the underlying webpage.
                    </div>
                </div>
            </div>
        </>
    )
}
