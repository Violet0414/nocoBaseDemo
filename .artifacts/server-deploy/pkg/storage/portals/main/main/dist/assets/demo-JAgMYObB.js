import{k as ee,r as i,dU as O,j as e,dV as B,dW as te,dP as se,dQ as ae,dL as oe,dM as re,dN as ne,v as n,au as ie,am as z,C as f,a as w,b as j,c as v,d as b,L as U,S as le,e as ce,f as de,g as ue,h as he,I as pe,dX as l,dY as E,aY as p,w as $,bU as m,B as g,dZ as F,d_ as I,P as me,E as xe,d$ as ge}from"./index-CN0Fpyvo.js";import{u as fe,a as V,R as y}from"./route-drawer-Dw4Dwp9A.js";import{P as N}from"./prompt-output-oG9aqAve.js";import{u as we}from"./use-route-surface-close-B_E_Nktd.js";import"./scrollable-D0luDtrn.js";/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const je=[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]],k=ee("arrow-right",je);function C(t){return`${t.pathname}${t.search??""}${t.hash??""}`}function ve(t){return{...t.state&&typeof t.state=="object"&&!Array.isArray(t.state)?t.state:{},routeSurfaceReturnTo:C(t)}}function be(t,s){const a=t&&typeof t=="object"&&!Array.isArray(t)?t.routeSurfaceReturnTo:void 0;return typeof a=="string"&&a.length>0?a:C(s)}function K({title:t,description:s,actions:a,children:o,closeLabel:u,closeTo:L,beforeClose:r,className:_,nested:M}){const T=i.useContext(O),X=fe(),Y=T>0,{open:P,setOpen:A,close:h,navigateAfterClose:Q}=V({closeTo:L,beforeClose:r,animated:!0}),Z=i.useCallback((x,J)=>{if(x){A(!0);return}J.cancel(),h()},[h,A]);return e.jsx(B.Provider,{value:h,children:e.jsx(O.Provider,{value:T+1,children:e.jsxs(te,{open:P,onOpenChange:Z,onOpenChangeComplete:x=>{x||Q()},children:[e.jsxs(se,{className:"pointer-events-none fixed inset-y-0 right-0 left-0 z-50 transition-[right] duration-200 ease-in-out md:right-(--route-overlay-inline-end)",style:X,children:[Y?e.jsx(ye,{open:P,onClose:h}):e.jsx(ae,{className:"pointer-events-auto absolute inset-0 bg-black/10 duration-150 supports-backdrop-filter:backdrop-blur-xs data-open:animate-in data-open:fade-in-0 data-closed:animate-out data-closed:fade-out-0",onClick:x=>{x.stopPropagation(),h()}}),e.jsxs(oe,{className:z("pointer-events-auto absolute top-1/2 left-1/2 flex max-h-[calc(100dvh-2rem)] w-full max-w-[calc(100%-2rem)] -translate-x-1/2 -translate-y-1/2 flex-col overflow-hidden rounded-xl bg-popover text-sm text-popover-foreground ring-1 ring-foreground/10 duration-150 outline-none sm:max-w-2xl data-open:animate-in data-open:fade-in-0 data-open:zoom-in-95 data-closed:animate-out data-closed:fade-out-0 data-closed:zoom-out-95",_),children:[e.jsxs("header",{className:"relative shrink-0 border-b px-5 py-4 pr-14 text-left",children:[e.jsxs("div",{className:"flex items-start justify-between gap-4",children:[e.jsxs("div",{className:"min-w-0 space-y-1",children:[e.jsx(re,{className:"font-heading truncate text-lg font-medium",children:t}),s?e.jsx(ne,{className:"text-sm text-muted-foreground",children:s}):null]}),a?e.jsx("div",{className:"flex shrink-0 items-center gap-2",children:a}):null]}),e.jsxs(n,{type:"button",variant:"ghost",size:"icon-sm",className:"absolute top-3 right-3",onClick:()=>void h(),children:[e.jsx(ie,{}),e.jsx("span",{className:"sr-only",children:u})]})]}),o]})]}),M]})})})}function ye({open:t,onClose:s}){return e.jsx("div",{role:"presentation","aria-hidden":"true",className:z("pointer-events-auto absolute inset-0 bg-black/10 transition-opacity duration-150 supports-backdrop-filter:backdrop-blur-xs",t?"opacity-100":"pointer-events-none opacity-0"),onClick:a=>{a.stopPropagation(),s()}})}function q({children:t,closeTo:s,beforeClose:a}){const{close:o}=V({closeTo:s,beforeClose:a,animated:!1});return e.jsx(B.Provider,{value:o,children:t})}const D=[{id:"drawer",number:"1",title:"Drawer route",description:"Keep the current page mounted and open one URL-backed drawer.",path:"drawer",routeShape:"Page → Drawer"},{id:"dialog",number:"2",title:"Dialog route",description:"Open focused content in a modal while preserving the page URL history.",path:"dialog",routeShape:"Page → Dialog"},{id:"page",number:"3",title:"Child page",description:"Replace the current page instead of rendering the child inside an overlay.",path:"page",routeShape:"Page → Child page"},{id:"nested-drawers",number:"4",title:"Second-level drawer",description:"Push the lower drawer outward and keep the top drawer at a stable size.",path:"drawer/second",routeShape:"Page → Drawer → Drawer"},{id:"page-drawer-dialog",number:"5",title:"Page, drawer, and dialog",description:"Compose different presentation types without coupling business content to them.",path:"page/drawer/dialog",routeShape:"Child page → Drawer → Dialog"},{id:"contextual-child-routes",number:"6",title:"Contextual child routes",description:"Open the same create, edit, and detail surfaces from a list or detail context without leaving the current workflow.",path:"contextual",routeShape:"List → Detail → Edit"}];function Ce(t,s){const a={drawer:"Keep the current page mounted and open the target content with RouteDrawer. Closing the drawer returns to the page route.",dialog:"Keep the current page mounted and open the target content with RouteDialog. The dialog route must be directly addressable and dismissible through the shared close lifecycle.",page:"Render the target content as a real child page with RoutePage. Register it as a page route branch rather than placing it inside a drawer outlet.","nested-drawers":"Create a parent RouteDrawer with an Outlet and pass the rendered child outlet through its nested prop. The second RouteDrawer must push the lower drawer outward, keep equal widths, and close back to the parent route.","page-drawer-dialog":"Render a RoutePage first, place a RouteDrawer route inside that page, then render a RouteDialog as the drawer's nested route. Closing each layer must return to the immediately lower URL.","contextual-child-routes":"Define the list as the host route and register create, edit, and show as relative child routes. Reuse the same business surface from both list and detail contexts, but keep each URL under the route that opened it. Do not navigate to a fixed top-level resource URL from a child context."}[t.id];return`Build ${s||"the requested workflow"} with the installed NocoBase route surfaces.

Scenario:
- ${t.routeShape}
- ${a}

Implementation requirements:
- Import RouteDrawer, RouteDialog, and RoutePage from @/extensions/nocobase-route-surfaces; import useRouteSurfaceClose from @nocobase/portal-sdk/routing when actions need to close the active surface.
- Define application-owned resource routes once with defineAppRoutes. resourceAction only binds a child path to the parent Refine resource's create, edit, or show URL; it does not choose a presentation.
- With the default automatic resource outlet, every resourceAction element must render a RouteDrawer or RouteDialog. Never place a plain full-page form or detail component there because it will render below the list.
- When a resource action must replace the list as a full page, set outlet: "manual" on the resource route and use an application-owned layout that renders or consumes useOutlet().
- Keep data loading, forms, ACL guards, route paths, and business copy in application-owned files.
- Keep business content independent from its presentation container so the same content can move between a drawer, dialog, or page.
- Every surface must have an explicit closeTo URL.
- Use nested React Router routes and Outlet only when the visual layer is genuinely nested.
- Treat create, edit, show, and related-content overlays as contextual child routes. Use relative paths and navigation from the current host route; do not use a fixed absolute URL that moves the user to another resource page.
- Reuse business content across hosts, but let each host route own its child surface and closeTo URL. A resource name alone is not enough to select the correct presentation URL.
- When opening a contextual child, preserve the complete host URL, including search and hash, in navigation state. Use it as closeTo and fall back to the resolved parent route for direct URL entry.
- A full child page must be a page route branch, not an Outlet rendered inside a drawer.
- For editable forms, use useRefineUnsavedChangesGuard, pass its beforeClose callback to the surface, render its confirmation node, and use useRouteSurfaceClose for Cancel and successful submission.
- Direct URL entry, refresh, browser back/forward, Escape, the close button, and backdrop dismissal must all restore the correct layer stack.
- Verify visually that no resource action page is appended below its parent list.
- Apply Refine CanAccess with an AccessDenied fallback to each business resource/action independently; do not rely on a parent list permission for unrelated child pages.

Deliver the complete route definitions and React components using the application's existing design system.`}function Re(){const[t,s]=i.useState("drawer"),[a,o]=i.useState("a customer detail workflow"),u=D.find(r=>r.id===t)??D[0],L=i.useMemo(()=>Ce(u,a),[u,a]);return e.jsxs(f,{children:[e.jsxs(w,{children:[e.jsx(j,{children:"Prompt generator"}),e.jsx(v,{children:"Generate a complete routing scenario, not just an isolated overlay component."})]}),e.jsxs(b,{className:"grid items-start gap-5 xl:grid-cols-[360px_minmax(0,1fr)]",children:[e.jsxs("div",{className:"space-y-4",children:[e.jsxs("div",{className:"space-y-2",children:[e.jsx(U,{htmlFor:"route-surface-scenario",children:"Scenario"}),e.jsxs(le,{value:t,onValueChange:r=>s(r),children:[e.jsx(ce,{id:"route-surface-scenario",className:"w-full",children:e.jsx(de,{})}),e.jsx(ue,{children:D.map(r=>e.jsxs(he,{value:r.id,children:[r.number,". ",r.title]},r.id))})]})]}),e.jsxs("div",{className:"space-y-2",children:[e.jsx(U,{htmlFor:"route-surface-target",children:"Business target"}),e.jsx(pe,{id:"route-surface-target",value:a,onChange:r=>o(r.target.value)})]})]}),e.jsx(N,{title:"Generated routing prompt",description:"Updates as you change the scenario and business target.",prompt:L,promptClassName:"min-h-80"})]})]})}const Ne=`export const appRoutes = defineAppRoutes([
  {
    name: "customers",
    path: "customers",
    lazy: () => import("./customers/list"),
    resource: { meta: { label: "Customers" } },
    children: [
      {
        name: "customers.create",
        path: "create",
        resourceAction: "create",
        lazy: () => import("./customers/create-route"),
      },
    ],
  },
]);

// ./customers/create-route.tsx
export default function CustomerCreateRoute() {
  return (
    <RouteDrawer
      title="Create customer"
      closeLabel="Close"
      closeTo="/customers"
    >
      <CustomerCreateForm />
    </RouteDrawer>
  );
}`,De=`function CustomerResourceLayout() {
  const childPage = useOutlet();
  return childPage ?? <CustomerList />;
}

export const appRoutes = defineAppRoutes([
  {
    name: "customers",
    path: "customers",
    outlet: "manual",
    element: <CustomerResourceLayout />,
    resource: { meta: { label: "Customers" } },
    children: [
      {
        name: "customers.create",
        path: "create",
        resourceAction: "create",
        lazy: () => import("./customers/create-page"),
      },
    ],
  },
]);`,ke=`export const appRoutes = defineAppRoutes([
  {
    name: "customers",
    path: "customers",
    lazy: () => import("./customers/list"),
    resource: { meta: { label: "Customers" } },
    children: [
      // These are contextual child routes. They stay under the host page.
      {
        name: "customers.create",
        path: "create",
        resourceAction: "create",
        lazy: () => import("./customers/create-route"),
      },
      {
        name: "customers.edit",
        path: "edit/:id",
        resourceAction: "edit",
        lazy: () => import("./customers/edit-route"),
      },
      {
        name: "customers.show",
        path: "show/:id",
        resourceAction: "show",
        lazy: () => import("./customers/show-route"),
        children: [
          {
            name: "customers.show.edit",
            path: "edit",
            // Contextual duplicate: do not register a second resourceAction.
            lazy: () => import("./customers/show-edit-route"),
          },
        ],
      },
    ],
  },
]);

// CustomerShowRoute renders useOutlet() through RouteDrawer's nested prop.
// From the list, use navigate("edit/42") or navigate("show/42").
// From CustomerShowRoute, use navigate("edit") for the contextual editor.
// Do not navigate to a fixed /customers/edit/42 URL from another host.`;function Le(){return e.jsxs("section",{className:"space-y-4",children:[e.jsxs("div",{className:"space-y-1",children:[e.jsx("h2",{className:"font-heading text-xl font-semibold",children:"Refine resource actions"}),e.jsxs("p",{className:"max-w-3xl text-sm text-muted-foreground",children:[e.jsx("code",{children:"resourceAction"})," registers the action URL. The resolved route component still decides whether that URL opens an overlay or replaces the list. Load page modules through the route's ",e.jsx("code",{children:"lazy"})," field, and add ACL and unsaved-change handling as shown in the installed Users example."]})]}),e.jsxs("div",{className:"grid gap-4 xl:grid-cols-3",children:[e.jsx(N,{title:"List + routed drawer",description:"Use the automatic resource outlet and let the child own RouteDrawer.",prompt:Ne,copyLabel:"Copy example",copiedLabel:"Copied",promptClassName:"min-h-96"}),e.jsx(N,{title:"Full page replaces the list",description:"Use a manual resource outlet when the action is a standalone page.",prompt:De,copyLabel:"Copy example",copiedLabel:"Copied",promptClassName:"min-h-96"}),e.jsx(N,{title:"Contextual child surfaces",description:"Reuse create, edit, and detail content while each host owns its nested route.",prompt:ke,copyLabel:"Copy example",copiedLabel:"Copied",promptClassName:"min-h-96"})]})]})}const S="/route-surfaces";function c(){const{pathname:t}=p(),s=t.indexOf(S);return s>=0?t.slice(0,s+S.length):S}function G(){const t=m(),s=p();return i.useCallback(a=>t(a,{state:ve(s)}),[s,t])}function H(){const t=p(),s=ge("..");return i.useRef(be(t.state,s)).current}function Be(){const t=m(),s=l();return e.jsxs(e.Fragment,{children:[e.jsxs("div",{className:"space-y-6",children:[e.jsxs("div",{className:"space-y-2",children:[e.jsx(g,{variant:"secondary",children:"Route surfaces"}),e.jsx("h1",{className:"font-heading text-3xl font-semibold tracking-tight",children:"URL-backed pages and overlays"}),e.jsx("p",{className:"max-w-3xl text-muted-foreground",children:"Keep business content independent from whether it appears as a page, drawer, dialog, or nested combination. Every preview below supports a direct URL and browser history."})]}),e.jsx("div",{className:"grid gap-4 lg:grid-cols-2 xl:grid-cols-3",children:D.map(a=>e.jsxs(f,{className:"flex flex-col",children:[e.jsxs(w,{children:[e.jsxs("div",{className:"flex items-center justify-between gap-3",children:[e.jsxs(g,{variant:"outline",children:["Scenario ",a.number]}),e.jsx("span",{className:"text-xs text-muted-foreground",children:a.routeShape})]}),e.jsx(j,{children:a.title}),e.jsx(v,{children:a.description})]}),e.jsx(b,{className:"mt-auto",children:e.jsxs(n,{type:"button",variant:"outline",className:"w-full",onClick:()=>t(a.path),children:["Open preview",e.jsx(k,{})]})})]},a.id))}),e.jsx(Le,{}),e.jsx(Re,{})]}),s]})}function ze(){const t=m(),s=l(),a=c();return e.jsx(y,{title:"Customer details",description:"A routed drawer keeps the scenario page mounted behind it.",closeLabel:"Close",closeTo:a,nested:s,children:e.jsx(d,{label:"Drawer",title:"Northwind renewal",description:"Business content does not know that it is rendered inside a drawer.",children:e.jsxs(n,{onClick:()=>t("second"),children:["Open second-level drawer",e.jsx(k,{})]})})})}function Ee(){const t=c();return e.jsx(y,{title:"Renewal activity",description:"The lower drawer is pushed outward and remains behind the layer mask.",closeLabel:"Close",closeTo:`${t}/drawer`,children:e.jsx(d,{label:"Second-level drawer",title:"Latest review",description:"Clicking this layer's backdrop closes only the top drawer."})})}function $e(){const t=c();return e.jsx(K,{title:"Approve renewal",description:"A modal route for a focused decision.",closeLabel:"Close",closeTo:t,children:e.jsx(d,{label:"Dialog",title:"Approval required",description:"The page stays mounted while the URL represents the active dialog."})})}function Fe(){const t=l(),s=c();return e.jsx(q,{closeTo:s,children:e.jsx(Se,{nested:t})})}function Se({nested:t}){const s=we(),a=m();return e.jsxs(e.Fragment,{children:[e.jsxs("div",{className:"space-y-6",children:[e.jsxs("div",{className:"flex flex-wrap items-start justify-between gap-4",children:[e.jsxs("div",{className:"space-y-2",children:[e.jsx(g,{variant:"secondary",children:"Child page"}),e.jsx("h1",{className:"font-heading text-3xl font-semibold tracking-tight",children:"Customer workspace"}),e.jsx("p",{className:"text-muted-foreground",children:"This route replaces the Demo home instead of rendering inside its Outlet."})]}),e.jsxs(n,{variant:"outline",onClick:()=>void s(),children:[e.jsx(F,{}),"Back to scenarios"]})]}),e.jsxs(f,{children:[e.jsxs(w,{children:[e.jsxs("div",{className:"flex items-center gap-2",children:[e.jsx(I,{className:"size-5 text-primary"}),e.jsx(j,{children:"Page-owned workflow"})]}),e.jsx(v,{children:"A page can still host routed overlays without becoming coupled to their content."})]}),e.jsx(b,{children:e.jsx(n,{onClick:()=>a("drawer"),children:"Open page drawer"})})]})]}),t]})}function Ie(){const t=m(),s=l(),a=c();return e.jsx(y,{title:"Customer activity",description:"This drawer belongs to the child page route.",closeLabel:"Close",closeTo:`${a}/page`,nested:s,children:e.jsx(d,{label:"Page drawer",title:"Renewal conversation",description:"Open a dialog above this drawer to test mixed presentation types.",children:e.jsxs(n,{onClick:()=>t("dialog"),children:["Open confirmation dialog",e.jsx(k,{})]})})})}function Ve(){const t=c();return e.jsx(K,{title:"Confirm follow-up",description:"The dialog is nested in the drawer route subtree.",closeLabel:"Close",closeTo:`${t}/page/drawer`,children:e.jsx(d,{label:"Nested dialog",title:"Schedule a follow-up?",description:"Closing returns to the drawer; closing the drawer then returns to the page."})})}function Ke(){const t=c(),s=l(),a=m();return e.jsx(q,{closeTo:t,children:e.jsxs("div",{className:"space-y-6",children:[e.jsxs("div",{className:"flex flex-wrap items-start justify-between gap-4",children:[e.jsxs("div",{className:"space-y-2",children:[e.jsx(g,{variant:"secondary",children:"Contextual child routes"}),e.jsx("h1",{className:"font-heading text-3xl font-semibold tracking-tight",children:"One surface, multiple host contexts"}),e.jsx("p",{className:"max-w-3xl text-muted-foreground",children:"Create, edit, and detail routes stay under the page that opened them. The same form and detail content can be reused without sending the user to another resource page."})]}),e.jsxs(n,{variant:"outline",onClick:()=>void a(t),children:[e.jsx(F,{}),"Back to scenarios"]})]}),s?null:e.jsxs(f,{children:[e.jsxs(w,{children:[e.jsx(j,{children:"Choose a host page"}),e.jsx(v,{children:"The list owns its child routes. Open the list preview to test create, edit, detail, and detail-to-edit navigation."})]}),e.jsx(b,{children:e.jsxs(n,{onClick:()=>a("list?status=renewal&page=2"),children:["Open customer list",e.jsx(k,{})]})})]}),s]})})}function qe(){const t=l(),s=G(),a=p();return e.jsxs(e.Fragment,{children:[e.jsxs(f,{children:[e.jsxs(w,{children:[e.jsxs("div",{className:"flex items-center gap-2",children:[e.jsx(I,{className:"size-5 text-primary"}),e.jsx(j,{children:"Customer list host"})]}),e.jsx(v,{children:"These actions use relative child navigation. The list remains the host when a surface opens."})]}),e.jsxs(b,{className:"space-y-4",children:[e.jsxs("div",{className:"rounded-lg border bg-muted/30 p-4",children:[e.jsx("div",{className:"font-medium",children:"Northwind renewal"}),e.jsxs("div",{className:"text-sm text-muted-foreground",children:["Current route: ",C(a)]})]}),e.jsxs("div",{className:"flex flex-wrap gap-2",children:[e.jsxs(n,{onClick:()=>s("create"),children:[e.jsx(me,{}),"Create"]}),e.jsxs(n,{variant:"outline",onClick:()=>s("edit/42"),children:[e.jsx($,{}),"Edit from list"]}),e.jsxs(n,{variant:"outline",onClick:()=>s("detail/42"),children:[e.jsx(xe,{}),"Open detail"]})]})]})]}),t]})}function Ge(){const t=l(),s=G(),{id:a}=E(),o=p(),u=H();return e.jsx(y,{title:"Customer details",description:"The detail surface is nested under the list host.",closeLabel:"Close",closeTo:u,nested:t,children:e.jsx(d,{label:"Detail child route",title:`Northwind renewal #${a??"42"}`,description:`Current route: ${C(o)}`,children:e.jsxs(n,{onClick:()=>s("edit"),children:[e.jsx($,{}),"Edit from detail"]})})})}function He(){return e.jsx(W,{mode:"create"})}function We(){return e.jsx(W,{mode:"edit"})}function W({mode:t}){const s=p(),{id:a}=E(),o=H();return e.jsx(y,{title:t==="create"?"Create customer":"Edit customer",description:"The same form surface can be hosted by different parent routes.",closeLabel:"Close",closeTo:o,children:e.jsx(d,{label:t==="create"?"Create child route":"Edit child route",title:t==="create"?"New customer":`Northwind renewal #${a??"42"}`,description:`Current route: ${C(s)}`,children:e.jsx("div",{className:"rounded-lg border border-dashed p-4 text-sm text-muted-foreground",children:"The parent route remains mounted while this reusable form is shown."})})})}function d({label:t,title:s,description:a,children:o}){return e.jsx("div",{className:"min-h-0 flex-1 overflow-y-auto px-5 py-5",children:e.jsxs("div",{className:"space-y-5",children:[e.jsx(g,{variant:"outline",children:t}),e.jsxs("div",{className:"space-y-2",children:[e.jsx("h2",{className:"text-xl font-semibold",children:s}),e.jsx("p",{className:"text-muted-foreground",children:a})]}),e.jsxs("div",{className:"grid gap-3 rounded-lg border bg-muted/30 p-4 sm:grid-cols-2",children:[e.jsx(R,{label:"Owner",value:"Ada Lovelace"}),e.jsx(R,{label:"Status",value:"In review"}),e.jsx(R,{label:"Value",value:"$48,000"}),e.jsx(R,{label:"Renewal",value:"September 30"})]}),o?e.jsx("div",{children:o}):null]})})}function R({label:t,value:s}){return e.jsxs("div",{className:"space-y-1",children:[e.jsx("div",{className:"text-xs text-muted-foreground",children:t}),e.jsx("div",{className:"font-medium",children:s})]})}export{He as DemoContextualCreateRoute,Ge as DemoContextualDetailRoute,We as DemoContextualEditRoute,Ke as DemoContextualHomeRoute,qe as DemoContextualListRoute,$e as DemoDialogRoute,ze as DemoDrawerRoute,Ve as DemoPageDrawerDialogRoute,Ie as DemoPageDrawerRoute,Fe as DemoPageRoute,Ee as DemoSecondDrawerRoute,Be as RouteSurfacesDemoHome};
