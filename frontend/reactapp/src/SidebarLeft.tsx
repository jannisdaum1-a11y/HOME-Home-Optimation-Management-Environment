import './SidebarLeft.css'

import assets from './assets/assets.json'

type AssetData = {
    image: string | null;
    [key: string]: unknown;
};
type AssetIconProps = {
    name: string,
    data: AssetData
}

function AssetIcon({name, data}: AssetIconProps){
    const image_path = data.image;
    return (
        <div className='AssetIcon' key={name} 
        draggable onDragStart={(e) => e.dataTransfer.setData("asset", name)}>
            <img src={image_path ?? ""} alt={name} draggable={false}/>
            <p>{name}</p>
        </div>
    )
}
function SidebarLeft() {
    return (
        <div className="SideBarLeft">
            {Object.entries(assets).map(([name, data]) => (
                <AssetIcon name={name} data={data}></AssetIcon>
            ))}
        </div>
    );
}

export default SidebarLeft