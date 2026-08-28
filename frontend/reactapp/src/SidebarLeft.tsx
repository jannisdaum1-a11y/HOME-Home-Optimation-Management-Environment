import './SidebarLeft.css'

import assets from './assets/assets.json'

const excludeAssets: string[] = ['Config', "EV"];

type AssetData = {
    image?: string | null;
    [key: string]: unknown;
};
type AssetIconProps = {
    name: string,
    data: AssetData,
    onAddAsset: (name: string) => void,
}

function AssetIcon({name, data, onAddAsset}: AssetIconProps){
    const image_path = data.image;
    return (
        <div className='AssetIcon' key={name} 
        draggable onDragStart={(e) => e.dataTransfer.setData("asset", name)}>
            <img src={image_path ?? ""} alt={name} draggable={false}/>
            <p>{name}</p>
            <button type="button" onClick={() => onAddAsset(name)}>Hinzufügen</button>
        </div>
    )
}
type SidebarLeftProps = {
    onAddAsset: (name: string) => void,
};

function SidebarLeft({onAddAsset}: SidebarLeftProps) {
    return (
        <div className="SideBarLeft">
            {Object.entries(assets).map(([name, data]) => (
                !excludeAssets.includes(name) &&
                <AssetIcon name={name} data={data} onAddAsset={onAddAsset}></AssetIcon>
            ))}
        </div>
    );
}

export default SidebarLeft